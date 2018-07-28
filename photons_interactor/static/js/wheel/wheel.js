/*
 * This work is licensed under NonCommercial-ShareAlike 4.0 International
 * (CC BY-NC-SA 4.0). The 'LIFX Colour Wheel' patented design as intellectual
 * property is used in this repository.
 *
 * LIFX has granted permission to use the 'LIFX Colour Wheel' design conditional
 * on use of the (CC BY-NC-SA 4.0) license.
 *
 * Commercial use the 'LIFX Colour Wheel' requires written consent from LIFX.
 * Submit enquiries to business@lifx.com
 */

import hskToColor from "../hsk-to-color.js";
import Tweener from "./tween.js";

import easingTypes from "tween-functions";
import React from "react";
import {
  Stage,
  Line,
  Layer,
  Rect,
  Group,
  Text,
  Circle,
  Wedge,
  Arc
} from "react-konva";

const whites = [
  [1500, "Candlelight"],
  [2000, "Sunset"],
  [2500, "Ultra Warm"],
  [2750, "Incandescent"],
  [3000, "Warm"],
  [3200, "Neutral Warm"],
  [3500, "Neutral"],
  [4000, "Cool"],
  [4500, "Cool Daylight"],
  [5000, "Soft Daylight"],
  [5500, "Daylight"],
  [6000, "Noon Daylight"],
  [6500, "Bright Daylight"],
  [7000, "Cloudy Daylight"],
  [7500, "Blue Daylight"],
  [8000, "Blue Overcast"],
  [8500, "Blue Water"],
  [9000, "Blue Ice"]
];

const normaldwhites = [whites[0]];
for (let i = 0; i < whites.length - 1; i++) {
  let diff = whites[i + 1][0] - whites[i][0];
  normaldwhites.push([
    Math.round(whites[i + 1][0] - diff / 2),
    whites[i + 1][1]
  ]);
}

function angle_to_kelvin(angle) {
  return Math.round(1500 + (9000 - 1500) * (angle / 360));
}

function kelvin_to_angle(kelvin) {
  return (kelvin - 1500) * 360 / (9000 - 1500);
}

function normal_hue(hue) {
  while (hue < 0) {
    hue += 360;
  }
  return hue % 360;
}

function getPos(el) {
  for (
    var lx = 0, ly = 0;
    el != null;
    lx += el.offsetLeft, ly += el.offsetTop, el = el.offsetParent
  );
  return { x: lx, y: ly };
}

class Power extends React.Component {
  constructor(props) {
    super(props);
    this.state = { on: props.on };
    props.events.onPowerChange = ::this.clicked;
  }

  clicked(click) {
    const new_on = !this.state.on;
    if (click !== false) {
      this.props.onClick();
    }
    this.setState({ on: new_on });
  }

  render() {
    const { center_x, center_y, inner_radius, outer_radius } = this.props;
    const arc_top = this.props.height - (outer_radius - inner_radius) / 2 - 5;
    return (
      <Group>
        <Arc
          onClick={::this.clicked}
          angle={70}
          rotation={90 - 35}
          x={center_x}
          y={center_y}
          fill="#4d5866"
          innerRadius={inner_radius}
          outerRadius={outer_radius}
        />
        <Arc
          onClick={::this.clicked}
          x={this.props.width / 2}
          y={arc_top}
          angle={280}
          rotation={-90 + 40}
          innerRadius={12}
          outerRadius={15}
          fill={this.state.on ? "#009EFD" : "white"}
        />
        <Line
          onClick={::this.clicked}
          points={[
            this.props.width / 2,
            arc_top - 10,
            this.props.width / 2,
            arc_top
          ]}
          stroke={this.state.on ? "#009EFD" : "white"}
          strokeWidth={3}
        />
      </Group>
    );
  }
}

class DraggableArc extends React.Component {
  clickArcs(e) {
    const offset = getPos(e.target.getStage().attrs.container);
    const s_x = e.evt.clientX - offset.x;
    const s_y = e.evt.clientY - offset.y;

    var nodes = e.target.getParent().getChildren();
    var point = { x: s_x, y: s_y };

    var hue = 0;
    for (var i = 0; i <= 360; i++) {
      if (nodes[i].intersects(point)) {
        hue = nodes[i].attrs.rotation;
        break;
      }
    }
    this.props.onClick(hue);
  }

  render() {
    const {
      hue,
      on,
      center_x,
      center_y,
      inner_radius,
      outer_radius,
      white
    } = this.props;

    const arcs = [];
    for (var angle = 0; angle <= 360; angle += 1) {
      var color = "hsl(" + angle + ", " + (on ? 100 : 30) + "%, 50%)";
      if (white) {
        color = hskToColor(angle, 0, angle_to_kelvin(angle));
      }
      arcs.push(
        <Arc
          key={angle}
          angle={3}
          rotation={angle}
          x={center_x}
          y={center_y}
          innerRadius={inner_radius}
          outerRadius={outer_radius}
          fill={color}
        />
      );
    }

    var cover_circle_gradient_stops = [
      0,
      on ? "white" : "rgba(255,255,255,0)",
      1,
      "rgba(255,255,255,0)"
    ];
    if (white) {
      let black_cover = on ? "rgba(255,255,255,0" : "rgba(0,0,0,0.3)";
      cover_circle_gradient_stops = [0, black_cover, 1, black_cover];
    }

    return (
      <Group
        ref={o => {
          this.props.refs.draggable_arcs = o;
        }}
        draggable={true}
        dragBoundFunc={pos => ({ x: center_x, y: center_y })}
        onDragStart={this.props.onDragStart}
        onDragMove={this.props.onDragMove}
        onDragEnd={this.props.onDragEnd}
        offset={{ x: center_x, y: center_y }}
        rotation={-((hue + 90) % 360)}
        x={center_x}
        y={center_y}
      >
        {arcs}
        <Arc
          angle={360}
          x={center_x}
          y={center_y}
          onClick={::this.clickArcs}
          innerRadius={inner_radius}
          outerRadius={outer_radius}
          fillRadialGradientStartRadius={inner_radius}
          fillRadialGradientEndRadius={outer_radius}
          fillRadialGradientColorStops={cover_circle_gradient_stops}
        />
      </Group>
    );
  }
}

class Brightness extends React.Component {
  componentDidMount() {
    this.props.refs.brightness_lines.move({
      x: 0,
      y: -(this.props.height * this.props.brightness)
    });
  }

  render() {
    const {
      refs,
      brightness,
      height,
      center_x,
      center_y,
      inner_radius,
      outer_radius
    } = this.props;

    const pos_y = center_y - height * brightness;

    const lines = [];
    for (let i = 0; i < 16; i++) {
      let y = i * (this.props.height / 15) + pos_y;
      let l = 100 - Math.round(100 * Math.abs(y - center_y) / center_y);
      let stroke = "hsl(0,0%," + l + "%)";
      lines.push({ i, y, stroke });
    }

    return (
      <Group>
        <Group
          clipFunc={ctx => {
            ctx.arc(center_x, center_y, inner_radius, 0, Math.PI * 2, false);
          }}
        >
          <Circle
            x={center_x}
            y={center_y}
            radius={inner_radius}
            fillRadialGradientStartRadius={inner_radius}
            fillRadialGradientEndRadius={outer_radius}
            fillRadialGradientColorStops={[0, "#6e7d91", 1, "#4d5866"]}
            fillRadialGradientStartPoint={{
              x: 0,
              y: 0
            }}
            fillRadialGradientEndPoint={{
              x: 90,
              y: 90
            }}
          />
          <Group
            ref={o => {
              refs.brightness_lines = o;
            }}
            draggable={true}
            dragBoundFunc={pos => {
              let y = pos.y;
              if (y > -(this.props.height * 0.01)) {
                y = -(this.props.height * 0.01);
              }

              if (y < -this.props.height) {
                y = -this.props.height;
              }

              return { x: 0, y: y };
            }}
            onDragMove={this.props.onDragMove}
          >
            <Rect
              x={0}
              y={0}
              width={this.props.width}
              height={this.props.height * 3}
            />
          </Group>
          <Group>
            {lines.map(l =>
              <Line
                key={l.i}
                points={[center_x - 10, l.y, center_x + 10, l.y]}
                stroke={l.stroke}
                strokeWidth={1}
              />
            )}
          </Group>
        </Group>
      </Group>
    );
  }
}

class SaturationControl extends React.Component {
  render() {
    const {
      center_x,
      center_y,
      inner_radius,
      outer_radius,
      on,
      hue,
      saturation
    } = this.props;

    var l = 1 - saturation;
    if (l > 0.8) {
      l = 0.8;
    }
    const white_color = "rgba(255,255,255," + l + ")";

    const color = "hsl(" + hue + ",100%,50%)";
    const min_y = 15;
    const max_y = center_y - inner_radius - 15;
    const y_pos = max_y - (max_y - min_y) * saturation;

    return (
      <Layer>
        <Line
          points={[
            center_x,
            center_y - outer_radius,
            center_x,
            center_y - inner_radius
          ]}
          stroke="black"
          strokeWidth={3}
        />
        <Circle
          x={center_x}
          y={y_pos}
          radius={15}
          fill={color}
          stroke={on ? "white" : "black"}
          strokeWidth={2}
        />
        <Circle
          ref={o => {
            this.props.refs.saturation_circle = o;
          }}
          draggable={true}
          dragBoundFunc={pos => {
            let y = pos.y;

            let min_y = 15;
            if (y < min_y) {
              y = min_y;
            }

            let max_y = center_y - inner_radius - 15;
            if (y > max_y) {
              y = max_y;
            }

            return { x: center_x, y: y };
          }}
          onDragMove={this.props.onDragMove}
          x={center_x}
          y={y_pos}
          radius={15}
          fill={white_color}
          stroke={on ? "white" : "black"}
          strokeWidth={2}
        />
      </Layer>
    );
  }
}

export class ColourPicker extends React.Component {
  constructor(props) {
    super(props);
    this.tweener = new Tweener(this);

    let hue = props.hue;
    if (props.white) {
      hue = kelvin_to_angle(props.kelvin);
    }

    this.state = Object.assign(
      {},
      {
        hue: hue,
        on: props.on,
        saturation: props.saturation,
        brightness: props.brightness
      },
      this.tweener.getInitialState()
    );
    this.events = {};

    this.last_angle = -hue * (Math.PI / 180);

    this.extra_refs = {};

    this.inner_radius = Math.round(this.props.height / 3.5);
    this.outer_radius = Math.round(this.props.height / 2);
    this.center_x = this.props.width / 2;
    this.center_y = this.props.height / 2;
  }

  static getDerivedStateFromProps(props, state) {
    let { kelvin, hue, on, saturation, brightness, white } = props;
    let isnewprops =
      state.oldprops === undefined ||
      (hue !== state.oldprops.hue ||
        on !== state.oldprops.on ||
        saturation !== state.oldprops.saturation ||
        brightness !== state.oldprops.brightness ||
        kelvin !== state.oldprops.kelvin ||
        white !== state.oldprops.white);

    if (isnewprops) {
      var colorhue = state.colorhue;

      if (white) {
        colorhue = hue;
        hue = kelvin_to_angle(kelvin);
      } else {
        hue = state.colorhue || hue;
      }

      return {
        hue,
        on,
        colorhue,
        saturation,
        brightness,
        isnewprops,
        oldprops: props
      };
    }

    return { isnewprops };
  }

  componentDidUpdate() {
    if (this.state.isnewprops) {
      this.last_angle = -this.state.hue * (Math.PI / 180);
    }
  }

  componentWillUnmount() {
    this.tweener.componentWillUnmount();
  }

  submit(payload) {
    var args = { duration: 0.3 };
    var components = {};

    if (
      payload.hue !== undefined ||
      payload.saturation != undefined ||
      payload.brightness != undefined
    ) {
      let hueval = payload.hue || this.state.hue;
      components.saturation = payload.saturation || this.state.saturation;
      components.brightness = payload.brightness || this.state.brightness;

      const sat = components.saturation.toFixed(2);
      const bright = components.brightness.toFixed(2);

      if (this.props.white) {
        components.kelvin = angle_to_kelvin(hueval);
        args.color =
          "saturation:0 kelvin:" + components.kelvin + " brightness:" + bright;
      } else {
        components.hue = normal_hue(hueval);
        args.color =
          "hue:" +
          components.hue.toFixed(2) +
          " saturation:" +
          sat +
          " brightness:" +
          bright;
      }
    }

    if (payload.power !== undefined) {
      args.power = payload.power ? "on" : "off";
    } else if (!this.state.on) {
      args.power = "on";
      this.setState({ on: true });
      this.events.onPowerChange(false);
    }

    if (args.power !== undefined) {
      components.on = args.power === "on";
    }

    this.props.submit(args, components);
  }

  power_clicked() {
    const new_on = !this.state.on;
    this.setState({ on: new_on });
    this.submit({ power: new_on });
  }

  dragstart(e) {
    const offset = getPos(e.target.getStage().attrs.container);
    this.h_x = e.evt.clientX - offset.x;
    this.h_y = e.evt.clientY - offset.y;
  }

  dragmove(e) {
    const offset = getPos(e.target.getStage().attrs.container);
    const s_x = e.evt.clientX - offset.x;
    const s_y = e.evt.clientY - offset.y;
    var s_rad = Math.atan2(s_y - this.center_y, s_x - this.center_x);
    s_rad -= Math.atan2(this.h_y - this.center_y, this.h_x - this.center_x);
    s_rad += this.last_angle;
    const hue = normal_hue(-(s_rad * (180 / Math.PI)));
    this.setState({ hue });
    this.submit({ hue });
  }

  dragend(e) {
    const offset = getPos(e.target.getStage().attrs.container);
    const s_x = e.evt.clientX - offset.x;
    const s_y = e.evt.clientY - offset.y;

    var s_rad = Math.atan2(s_y - this.center_y, s_x - this.center_x);
    s_rad -= Math.atan2(this.h_y - this.center_y, this.h_x - this.center_x);
    s_rad += this.last_angle;
    this.last_angle = s_rad;
  }

  drag_brightness(e) {
    const brightness = -(
      this.extra_refs.brightness_lines.attrs.y / this.props.height
    );
    this.setState({ brightness });
    this.submit({ brightness });
  }

  drag_saturation(e) {
    const min_y = 15;
    const max_y = this.center_y - this.inner_radius - 15;

    const saturation =
      (max_y - this.extra_refs.saturation_circle.attrs.y) / (max_y - min_y);

    this.setState({ saturation });
    this.submit({ saturation });
  }

  clickColours(hue) {
    var to_hue = hue;
    if (this.state.hue < hue && hue - this.state.hue > 180) {
      to_hue = hue - 360;
    } else if (this.state.hue > hue && this.state.hue - hue > 180) {
      to_hue = hue + 360;
    }

    this.tweener.tweenState("hue", {
      easing: easingTypes.easeInOutQuad,
      duration: 500,
      endValue: to_hue,
      onEnd: () => this.setState({ hue })
    });
    this.submit({ hue });

    // And make sure when we start dragging again
    // It continues from the same place
    this.last_angle = -hue * (Math.PI / 180);
  }

  render() {
    const hue = this.tweener.getTweeningValue("hue");
    const brightness = Math.round(this.state.brightness * 100);
    const kelvin = angle_to_kelvin(hue);

    let text =
      "Color " + Math.round(normal_hue(hue)) + "° - " + brightness + "%";
    if (this.props.white) {
      text = "Kelvin " + kelvin + " - " + brightness + "%";
    }

    let kelvinText = "";
    if (this.props.white) {
      for (var i = 0; i < normaldwhites.length; i++) {
        if (kelvin >= normaldwhites[i][0]) {
          kelvinText = normaldwhites[i][1];
        }
      }
    }

    var style = this.props.style || {};
    return (
      <div style={style}>
        <Stage width={this.props.width} height={this.props.white ? 60 : 30}>
          <Layer>
            <Text
              fontSize={24}
              text={text}
              align="center"
              width={this.props.width}
            />
            {this.props.white
              ? <Text
                  y={30}
                  fontSize={24}
                  text={kelvinText}
                  align="center"
                  width={this.props.width}
                />
              : null}
          </Layer>
        </Stage>
        <Stage width={this.props.width} height={this.props.height}>
          <Layer>
            <Brightness
              refs={this.extra_refs}
              center_x={this.center_x}
              center_y={this.center_y}
              inner_radius={this.inner_radius}
              width={this.props.width}
              height={this.props.height}
              brightness={this.state.brightness}
              onDragMove={::this.drag_brightness}
            />
          </Layer>
          <Layer>
            <DraggableArc
              white={this.props.white}
              on={this.state.on}
              hue={this.tweener.getTweeningValue("hue")}
              inner_radius={this.inner_radius}
              outer_radius={this.outer_radius}
              refs={this.extra_refs}
              center_x={this.center_x}
              center_y={this.center_y}
              onClick={::this.clickColours}
              onDragStart={::this.dragstart}
              onDragMove={::this.dragmove}
              onDragEnd={::this.dragend}
            />
            <Power
              on={this.state.on}
              onClick={::this.power_clicked}
              events={this.events}
              width={this.props.width}
              height={this.props.height}
              center_x={this.center_x}
              center_y={this.center_y}
              inner_radius={this.inner_radius}
              outer_radius={this.outer_radius}
            />
          </Layer>
          {this.props.white
            ? <Layer>
                <Line
                  points={[
                    this.center_x,
                    this.center_y - this.outer_radius,
                    this.center_x,
                    this.center_y - this.inner_radius
                  ]}
                  stroke="black"
                  strokeWidth={3}
                />
              </Layer>
            : <SaturationControl
                center_x={this.center_x}
                center_y={this.center_y}
                inner_radius={this.inner_radius}
                outer_radius={this.outer_radius}
                onDragMove={::this.drag_saturation}
                refs={this.extra_refs}
                on={this.state.on}
                hue={this.tweener.getTweeningValue("hue")}
                saturation={this.state.saturation}
              />}
        </Stage>
      </div>
    );
  }
}
