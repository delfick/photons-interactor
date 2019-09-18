from photons_tile_paint.animation import (
    coords_for_horizontal_line,
    put_characters_on_canvas,
    canvas_to_msgs,
)
from photons_themes.theme import ThemeColor as Color
from photons_control.tile import orientations_from
from photons_tile_paint.font.dice import dice
from photons_messages import TileMessages
from photons_themes.canvas import Canvas

import colorsys
import math


def make_rgb_and_color_pixels(canvas, length):
    rgb_made = []
    color_made = []

    for msg in canvas_to_msgs(canvas, coords_for_horizontal_line[:length], duration=1, acks=True):
        nxt = []
        for c in msg.colors:
            if c.saturation > 0:
                rgb = colorsys.hsv_to_rgb(c.hue / 360, c.saturation, c.brightness)
                rgb = tuple(int(p * 255) for p in rgb)
            else:
                if c.brightness < 0.01:
                    rgb = (0, 0, 0)
                else:
                    rgb = convert_K_to_RGB(c.kelvin)

            nxt.append(f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}")
        rgb_made.append(nxt)
        color_made.append([c.as_dict() for c in msg.colors])

    return rgb_made, color_made


async def tile_dice(target, serials, afr, **kwargs):
    canvas = Canvas()

    def default_color_func(i, j):
        if j == -3:
            return Color(0, 1, 0.4, 3500)
        return Color(0, 0, 0, 3500)

    canvas.set_default_color_func(default_color_func)

    numbers = ["1", "2", "3", "4", "5"]
    characters = [dice[n] for n in numbers]
    color = Color(100, 1, 1, 3500)
    put_characters_on_canvas(canvas, characters, coords_for_horizontal_line, color)

    orientations = {}
    async for pkt, _, _ in target.script(TileMessages.GetDeviceChain()).run_with(
        serials, afr, **kwargs
    ):
        if pkt | TileMessages.StateDeviceChain:
            orientations[pkt.serial] = orientations_from(pkt)

    made, _ = make_rgb_and_color_pixels(canvas, 5)

    msgs = []
    for serial in serials:
        os = orientations.get(serial)
        for msg in canvas_to_msgs(
            canvas, coords_for_horizontal_line, duration=1, acks=True, orientations=os
        ):
            msg.target = serial
            msgs.append(msg)

    await target.script(msgs).run_with_all(None, afr, **kwargs)
    return made


def convert_K_to_RGB(colour_temperature):
    """
    Converts from K to RGB, algorithm courtesy of
    http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
    Python translation from https://gist.github.com/petrklus/b1f427accdf7438606a6
    """
    if colour_temperature < 2500:
        colour_temperature = 2500
    elif colour_temperature > 9000:
        colour_temperature = 9000

    tmp_internal = colour_temperature / 100.0

    if tmp_internal <= 66:
        red = 255
    else:
        tmp_red = 329.698727446 * math.pow(tmp_internal - 60, -0.1332047592)
        if tmp_red < 0:
            red = 0
        elif tmp_red > 255:
            red = 255
        else:
            red = tmp_red

    if tmp_internal <= 66:
        tmp_green = 99.4708025861 * math.log(tmp_internal) - 161.1195681661
        if tmp_green < 0:
            green = 0
        elif tmp_green > 255:
            green = 255
        else:
            green = tmp_green
    else:
        tmp_green = 288.1221695283 * math.pow(tmp_internal - 60, -0.0755148492)
        if tmp_green < 0:
            green = 0
        elif tmp_green > 255:
            green = 255
        else:
            green = tmp_green

    if tmp_internal >= 66:
        blue = 255
    elif tmp_internal <= 19:
        blue = 0
    else:
        tmp_blue = 138.5177312231 * math.log(tmp_internal - 10) - 305.0447927307
        if tmp_blue < 0:
            blue = 0
        elif tmp_blue > 255:
            blue = 255
        else:
            blue = tmp_blue

    return int(red), int(green), int(blue)


class White:
    pass


class Black:
    pass


class StyleMaker:
    def __init__(self):
        self.styles = iter(self.compute_styles())

    def make_color(self, hue):
        if hue is White:
            return Color(0, 0, 1, 4500)
        elif hue is Black:
            return Color(0, 0, 0, 3500)
        else:
            return Color(hue, 1, 1, 3500)

    def compute_styles(self):
        colors = [0, 50, 100, 150, 180, 250, 300, White]
        shifted = colors[2:] + colors[:2]

        while True:
            for color in colors:
                yield "color", color

            for color in colors:
                yield "split", color

            for color in colors:
                yield "cross", (color,)

            for color in colors:
                yield "square", (color,)

            for h1, h2 in zip(colors, shifted):
                yield "square", (h1, h2)

            for h1, h2 in zip(colors, shifted):
                yield "cross", (h1, h2)

    @property
    def next_style(self):
        return next(self.styles)

    def set_canvas(self, canvas, length):
        for i in range(length):
            typ, options = self.next_style
            (left_x, top_y), (width, height) = coords_for_horizontal_line[i]
            if typ == "color":
                self.set_color(canvas, left_x, top_y, width, height, options)

            elif typ == "split":
                self.set_split(canvas, left_x, top_y, width, height, options)

            elif typ == "cross":
                self.set_cross(canvas, left_x, top_y, width, height, *options)

            else:
                self.set_square(canvas, left_x, top_y, width, height, *options)

    def set_color(self, canvas, left_x, top_y, width, height, hue):
        for i in range(left_x, left_x + width):
            for j in range(top_y - height, top_y + 1):
                canvas[(i, j)] = self.make_color(hue)

    def set_split(self, canvas, left_x, top_y, width, height, hue):
        for i in range(left_x, left_x + width):
            h = Black
            if i > left_x + width / 2:
                h = hue
            for j in range(top_y - height, top_y + 1):
                canvas[(i, j)] = self.make_color(h)

    def set_cross(self, canvas, left_x, top_y, width, height, hue1, hue2=None):
        i = left_x
        j = top_y
        while i < left_x + width and j > top_y - height:
            canvas[(i, j)] = self.make_color(hue1)
            i += 1
            j -= 1

        i = left_x + width - 1
        j = top_y
        while i >= left_x and j > top_y - height:
            h = hue2 if hue2 is not None else hue1
            canvas[(i, j)] = self.make_color(h)
            i -= 1
            j -= 1

    def set_square(self, canvas, left_x, top_y, width, height, hue1, hue2=None):
        i = left_x
        j = top_y
        direction = "right"

        while (i, j) not in canvas:
            canvas[(i, j)] = self.make_color(hue1)

            if direction == "right":
                if i == left_x + width - 1:
                    j -= 1
                    direction = "down"
                else:
                    i += 1
            elif direction == "down":
                if j == top_y - height + 1:
                    i -= 1
                    direction = "left"
                else:
                    j -= 1
            elif direction == "left":
                if i == left_x:
                    j += 1
                    direction = "up"
                else:
                    i -= 1
            elif direction == "up":
                j += 1

        if hue2 is None:
            return

        start_x = i = left_x + (width // 2) - 1
        start_y = j = top_y - (width // 2) + 1
        direction = "right"
        while (i, j) not in canvas:
            canvas[(i, j)] = self.make_color(hue2)

            if direction == "right":
                if i == start_x + 1:
                    j -= 1
                    direction = "down"
                else:
                    i += 1
            elif direction == "down":
                if j == start_y - 1:
                    i -= 1
                    direction = "left"
                else:
                    j -= 1
            elif direction == "left":
                if i == start_x:
                    j += 1
                    direction = "up"
                else:
                    i -= 1
            elif direction == "up":
                j += 1
