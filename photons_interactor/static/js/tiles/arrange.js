import { Stage, Layer, Text, Rect } from "react-konva";
import { withSize } from "react-sizeme";
import { connect } from "react-redux";

@withSize({ monitorHeight: true })
@connect((state, ownProps) => ({ pixels: state.tiles.pixels }))
export class TilesArranger extends React.Component {
  render() {
    var { width, height } = this.props.size;
    var { pixels } = this.props;

    var tiles = [];
    Object.keys(pixels).map(serial => {
      pixels[serial].map(tile => {
        tiles.push(tile);
      });
    });

    var pixelWidth = Math.floor(width / (tiles.length * 9));

    var pixels = [];
    tiles.map((tile, i) => {
      var start_x = i * 9 * pixelWidth;
      var start_y = 0;

      tile.map((pixel, j) => {
        var x = start_x + (j % 8) * pixelWidth;
        var y = start_y + Math.floor(j / 8) * pixelWidth;
        pixels.push({
          width: pixelWidth,
          height: pixelWidth,
          x,
          y,
          fill: pixel
        });
      });
    });

    console.log(pixels);

    return (
      <Stage
        ref="child"
        width={width}
        height={height}
        style={{ margin: "20px" }}
        fill="red"
      >
        <Layer>
          <Rect width={width} height={height} fill="#e6e6e6" />
        </Layer>
        <Layer>
          {pixels.map((opts, i) => (
            <Rect key={i} {...opts} />
          ))}
        </Layer>
      </Stage>
    );
  }
}
