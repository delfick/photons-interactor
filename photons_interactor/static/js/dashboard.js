import { DevicesState } from "./device/state.js";
import { Bulb } from "./device/component.js";
import { ShowError } from "./error.js";

import { connect } from "react-redux";
import PropTypes from "prop-types";
import React from "react";

import CircularProgress from "@material-ui/core/CircularProgress";
import { withStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Grid from "@material-ui/core/Grid";

const styles = theme => ({
  devices: {
    flexGrow: 1,
    marginTop: "10px"
  }
});

var dashconnector = connect((state, ownProps) => ({
  error: state.devices.error,
  serials: state.devices.serials,
  loading: state.devices.loading
}));
const Dashboard = dashconnector(
  ({ error, loading, serials, width, classes, spacing, dispatch }) =>
    <div>
      <Typography variant="display2">Devices</Typography>
      <ShowError error={error} clearer={DevicesState.ClearError()} />
      <Grid container className={classes.devices} spacing={16}>
        <Grid item xs={12}>
          <Grid
            container
            className={classes.demo}
            justify="center"
            spacing={16}
          >
            {loading ? <CircularProgress /> : null}
            {serials.map(serial =>
              <Grid key={serial} item>
                <Bulb serial={serial} />
              </Grid>
            )}
          </Grid>
        </Grid>
      </Grid>
    </div>
);

Dashboard.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(styles)(Dashboard);
