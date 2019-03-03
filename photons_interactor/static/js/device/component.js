import { SelectionState } from "../selection/state.js";

import { connect } from "react-redux";

import CircularProgress from "@material-ui/core/CircularProgress";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import Card from "@material-ui/core/Card";

const styles = theme => ({
  devices: {
    flexGrow: 1,
    marginTop: "10px"
  }
});

var bulbconnector = connect((state, ownProps) => ({
  data: state.devices.devices[ownProps.serial],
  selected: state.selection.selection[ownProps.serial]
}));
const Bulb = bulbconnector(({ dispatch, serial, data, selected }) => (
  <Card
    data-cy="bulb"
    style={selected ? { backgroundColor: "#0000ff14" } : undefined}
    onClick={() => {
      dispatch(SelectionState.ToggleSelection({ serial }));
    }}
  >
    <CardContent>
      <Typography component="p">{serial}</Typography>
      {!data ? (
        <CircularProgress size={20} />
      ) : (
        <BulbData serial={serial} data={data} />
      )}
    </CardContent>
  </Card>
));

const BulbData = ({ serial, data }) => (
  <Typography component="p" data-cy="bulb-label">
    {data.label}
  </Typography>
);

export { Bulb };
