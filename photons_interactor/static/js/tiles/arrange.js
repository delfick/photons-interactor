import { TilesState } from "./state.js";

import { Stage, Layer, Text, Rect, Group, Line } from "react-konva";
import { withSize } from "react-sizeme";
import { connect } from "react-redux";

function getPos(el) {
  for (
    var lx = 0, ly = 0;
    el != null;
    lx += el.offsetLeft, ly += el.offsetTop, el = el.offsetParent
  );
  return { x: lx, y: ly };
}

function x_y_for_evt(evt, offset) {
  var s_x, s_y;
  if (evt.clientX === undefined) {
    s_x = evt.changedTouches[0].clientX - offset.x;
    s_y = evt.changedTouches[0].clientY - offset.y;
  } else {
    s_x = evt.clientX - offset.x;
    s_y = evt.clientY - offset.y;
  }
  return [s_x, s_y];
}

const TilePixels = connect((state, ownProps) => ({
  pixels: state.tiles.by_serial[ownProps.serial].pixels[ownProps.tile_index]
}))(({ dispatch, pixels, pixelWidth, lineWidth, tileWidth }) => (
  <Group>
    {pixels.map((pixel, j) => {
      var x = (j % 8) * pixelWidth;
      var y = Math.floor(j / 8) * pixelWidth;
      return (
        <Rect
          key={j}
          width={pixelWidth}
          height={pixelWidth}
          x={x}
          y={y}
          fill={pixel}
        />
      );
    })}
    <Line
      stroke="white"
      strokeWidth={lineWidth}
      points={[0, 0, tileWidth, 0, tileWidth, tileWidth, 0, tileWidth, 0, 0]}
    />
  </Group>
));

@connect()
class Tile extends React.Component {
  onDragEnd(e) {
    var left_x = (this.newx - this.props.zero_x) / this.props.pixelWidth;
    var top_y = (this.props.zero_y - this.newy) / this.props.pixelWidth;
    this.props.dispatch(
      TilesState.ChangeCoords(
        this.props.serial,
        this.props.tile_index,
        left_x,
        top_y
      )
    );
  }

  dragBound(pos) {
    var newpos = {
      x: pos.x - ((pos.x - this.props.zero_x) % this.props.pixelWidth),
      y: pos.y - ((pos.y - this.props.zero_y) % this.props.pixelWidth)
    };
    this.newx = newpos.x;
    this.newy = newpos.y;
    return newpos;
  }

  render() {
    var {
      start_x,
      start_y,
      pixels,
      tile_index,
      serial,
      pixelWidth,
      lineWidth,
      tileWidth,
      dispatch
    } = this.props;

    return (
      <Group
        ref="group"
        x={start_x}
        y={start_y}
        draggable={true}
        onDragEnd={this.onDragEnd.bind(this)}
        dragBoundFunc={this.dragBound.bind(this)}
        onClick={() => dispatch(TilesState.Highlight(serial, tile_index))}
        onTap={() => dispatch(TilesState.Highlight(serial, tile_index))}
      >
        <TilePixels
          serial={serial}
          tile_index={tile_index}
          pixelWidth={pixelWidth}
          lineWidth={lineWidth}
          tileWidth={tileWidth}
        />
      </Group>
    );
  }
}

@connect((state, ownProps) => ({ by_serial: state.tiles.by_serial }))
class Tiles extends React.Component {
  render() {
    var { pixelWidth, tileWidth, zero_x, zero_y, by_serial } = this.props;

    var tiles = [];
    var lineWidth = Math.max(Math.floor(pixelWidth / 2), 1);

    Object.keys(by_serial).map(serial => {
      var coords = by_serial[serial].coords;
      by_serial[serial].pixels.map((tile, i) => {
        tiles.push([serial, coords[i], i]);
      });
    });

    var rects = [];
    tiles.map(([serial, [user_x, user_y], i]) => {
      var start_x = zero_x + user_x * pixelWidth;
      var start_y = zero_y - user_y * pixelWidth;

      rects.push(
        <Tile
          key={serial + i}
          serial={serial}
          zero_x={zero_x}
          zero_y={zero_y}
          serial={serial}
          tile_index={i}
          start_x={start_x}
          start_y={start_y}
          tileWidth={tileWidth}
          pixelWidth={pixelWidth}
          lineWidth={lineWidth}
        />
      );
    });

    return <Layer>{rects}</Layer>;
  }
}

@connect()
@withSize({ monitorHeight: true })
export class TilesArranger extends React.Component {
  constructor(props) {
    super(props);
    this.tileoffsets = {};

    this.state = {
      zero_x: Math.floor(props.size.width / 2),
      zero_y: Math.floor(props.size.height / 2) - 100
    };
  }

  drag_grid_start(e) {
    const offset = getPos(e.target.getStage().attrs.container);
    const [s_x, s_y] = x_y_for_evt(e.evt, offset);
    this.grid_x = s_x;
    this.grid_y = s_y;
    this.grid_start_offset = {
      zero_x: this.state.zero_x,
      zero_y: this.state.zero_y
    };
  }

  drag_grid(e) {
    const offset = getPos(e.target.getStage().attrs.container);
    const [s_x, s_y] = x_y_for_evt(e.evt, offset);
    var diffx = this.grid_x - s_x;
    var diffy = this.grid_y - s_y;
    this.setState({
      zero_x: this.grid_start_offset.zero_x - diffx,
      zero_y: this.grid_start_offset.zero_y - diffy
    });
  }

  clickExpander(e) {
    this.props.dispatch(TilesState.ToggleArrangerExpand());
  }

  render() {
    var { width, height } = this.props.size;

    var pixelWidth = Math.max(Math.ceil(width / 160), 6);
    var tileWidth = pixelWidth * 8;

    var grid = [
      <Line
        key="centerx0"
        strokeWidth={2}
        stroke="red"
        points={[this.state.zero_x, 0, this.state.zero_x, height]}
      />,
      <Line
        key="centery0"
        strokeWidth={2}
        stroke="red"
        points={[0, this.state.zero_y, width, this.state.zero_y]}
      />
    ];

    for (
      var i = this.state.zero_x + tileWidth;
      i <= width + tileWidth * 2;
      i += tileWidth
    ) {
      if (i > 0) {
        grid.push(
          <Line
            key={"rcol" + i}
            strokeWidth={1}
            stroke="#868686"
            points={[i, 0, i, height]}
          />
        );
      }
    }

    for (
      var i = this.state.zero_x - tileWidth;
      i >= -tileWidth * 2;
      i -= tileWidth
    ) {
      if (i < width) {
        grid.push(
          <Line
            key={"lcol" + i}
            strokeWidth={1}
            stroke="#868686"
            points={[i, 0, i, height]}
          />
        );
      }
    }

    for (
      var i = this.state.zero_y + tileWidth;
      i <= height + tileWidth * 2;
      i += tileWidth
    ) {
      if (i > 0) {
        grid.push(
          <Line
            key={"trow" + i}
            strokeWidth={1}
            stroke="#868686"
            points={[0, i, width, i]}
          />
        );
      }
    }

    for (
      var i = this.state.zero_y - tileWidth;
      i >= -tileWidth * 2;
      i -= tileWidth
    ) {
      if (i < height) {
        grid.push(
          <Line
            key={"bcol" + i}
            strokeWidth={1}
            stroke="#868686"
            points={[0, i, width, i]}
          />
        );
      }
    }

    return (
      <Stage
        ref="child"
        width={width}
        height={height}
        style={{ margin: "20px" }}
        fill="red"
      >
        <Layer>
          <Rect
            width={width}
            height={height}
            fill="#e6e6e6"
            draggable={true}
            dragBoundFunc={pos => ({ x: 0, y: 0 })}
            onDragMove={this.drag_grid.bind(this)}
            onDragStart={this.drag_grid_start.bind(this)}
          />
        </Layer>
        <Layer>{grid}</Layer>
        <Tiles
          zero_x={this.state.zero_x}
          zero_y={this.state.zero_y}
          pixelWidth={pixelWidth}
          tileWidth={tileWidth}
        />
        <Layer>
          <Group
            onClick={this.clickExpander.bind(this)}
            onTap={this.clickExpander.bind(this)}
          >
            <Rect
              width={40}
              height={40}
              x={width - 40}
              y={0}
              fill="#ffffff5c"
            />
            <Line
              strokeWidth={3}
              stroke="black"
              points={[
                width - 35,
                5,
                width - 5,
                5,
                width - 5,
                35,
                width - 35,
                35,
                width - 35,
                5
              ]}
            />
            <Line
              strokeWidth={3}
              stroke="black"
              points={[
                width - 35,
                25,
                width - 25,
                25,
                width - 25,
                35,
                width - 35,
                35,
                width - 35,
                25
              ]}
            />
          </Group>
        </Layer>
      </Stage>
    );
  }
}
