from photons_app.errors import FoundNoDevices

from photons_tile_paint.animation import (
      coords_for_horizontal_line
    , tile_serials_from_reference, put_characters_on_canvas
    , canvas_to_msgs, orientations_from
    )
from photons_themes.theme import ThemeColor as Color
from photons_tile_paint.font.dice import dice
from photons_messages import TileMessages
from photons_themes.canvas import Canvas

import colorsys
import math

async def tile_dice(target, reference, afr, **kwargs):
    serials = await tile_serials_from_reference(target, reference, afr)
    if not serials:
        raise FoundNoDevices("Didn't find any tiles")

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
    async for pkt, _, _ in target.script(TileMessages.GetDeviceChain()).run_with(serials, afr, **kwargs):
        if pkt | TileMessages.StateDeviceChain:
            orientations[pkt.serial] = orientations_from(pkt)

    made = []
    for msg in canvas_to_msgs(canvas, coords_for_horizontal_line, duration=1, acks=True):
        nxt = []
        for c in msg.kwargs["colors"]:
            if c.saturation > 0:
                rgb = colorsys.hsv_to_rgb(c.hue / 360, c.saturation, c.brightness)
                rgb = tuple(int(p * 255) for p in rgb)
            else:
                if c.brightness < 0.01:
                    rgb = (0, 0, 0)
                else:
                    rgb = convert_K_to_RGB(c.kelvin)

            nxt.append(f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}")
        made.append(nxt)

    msgs = []
    for serial in serials:
        os = orientations.get(serial)
        for msg in canvas_to_msgs(canvas, coords_for_horizontal_line, duration=1, acks=True, orientations=os):
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

    if tmp_internal <=66:
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
