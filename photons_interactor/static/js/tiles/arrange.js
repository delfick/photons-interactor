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

@withSize({ monitorHeight: true })
@connect((state, ownProps) => ({ by_serial: state.tiles.by_serial }))
export class TilesArranger extends React.Component {
  constructor(props) {
    super(props);
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

  render() {
    var { width, height } = this.props.size;
    var { by_serial } = this.props;

    var tiles = [];
    Object.keys(by_serial).map(serial => {
      var coords = by_serial[serial].coords;
      by_serial[serial].pixels.map((tile, i) => {
        tiles.push([tile, coords[i]]);
      });
    });

    var pixelWidth = Math.max(Math.ceil(width / 160), 6);
    var lineWidth = Math.max(Math.floor(pixelWidth / 2), 1);
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
      i <= width + tileWidth * 2;
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
      if (i < width) {
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

    var rects = [];
    tiles.map(([tile, [user_x, user_y]], i) => {
      var pixels = [];
      var start_x = this.state.zero_x + user_x * pixelWidth;
      var start_y = this.state.zero_y - user_y * pixelWidth;

      rects.push(
        <Group key={i} x={start_x} y={start_y}>
          {tile.map((pixel, j) => {
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
            points={[
              0,
              0,
              tileWidth,
              0,
              tileWidth,
              tileWidth,
              0,
              tileWidth,
              0,
              0
            ]}
          />
        </Group>
      );
    });

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
        <Layer>{rects}</Layer>
      </Stage>
    );
  }
}
