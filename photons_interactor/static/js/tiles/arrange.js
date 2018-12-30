import { Stage, Layer, Text } from "react-konva";

export class TilesArranger extends React.Component {
  render() {
    return (
      <Stage width={300} height={300} style={{ margin: "20px" }}>
        <Layer>
          <Text
            fontSize={24}
            text="To be constructed"
            align="center"
            width={300}
          />
        </Layer>
      </Stage>
    );
  }
}
