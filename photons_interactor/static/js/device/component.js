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
  data: state.devices.devices[ownProps.serial]
}));
const Bulb = bulbconnector(({ serial, data }) =>
  <Card>
    <CardContent>
      <Typography component="p">
        {serial}
      </Typography>
      {!data
        ? <CircularProgress size={20} />
        : <BulbData serial={serial} data={data} />}
    </CardContent>
  </Card>
);

const BulbData = ({ serial, data }) =>
  <Typography component="p">
    {data.label}
  </Typography>;

export { Bulb };
