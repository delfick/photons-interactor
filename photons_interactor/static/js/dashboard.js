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
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import RefreshIcon from "@material-ui/icons/Refresh";
import Divider from "@material-ui/core/Divider";
import Button from "@material-ui/core/Button";

const styles = theme => ({
  devices: {
    flexGrow: 1,
    marginTop: "10px"
  },
  bar: { flexGrow: 1 },
  devicesTitle: {
    borderRight: "0.1em solid black",
    padding: "8px 16px 8px 0px"
  }
});

const DashboardBar = withStyles(styles)(
  connect((state, ownProps) => ({}))(({ classes, dispatch }) => (
    <div className={classes.bar}>
      <AppBar position="static" color="default">
        <Toolbar>
          <Typography
            className={classes.devicesTitle}
            variant="title"
            color="inherit"
          >
            Devices
          </Typography>
          <Divider />
          <Button onClick={e => dispatch(DevicesState.Refresh())}>
            <RefreshIcon />
          </Button>
        </Toolbar>
      </AppBar>
    </div>
  ))
);

var dashconnector = connect((state, ownProps) => ({
  error: state.devices.error,
  serials: state.devices.serials,
  loading: state.devices.loading
}));
const Dashboard = dashconnector(
  ({ error, loading, serials, width, classes, spacing, dispatch }) => (
    <div>
      <DashboardBar />
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
            {serials.map(serial => (
              <Grid key={serial} item>
                <Bulb serial={serial} />
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </div>
  )
);

Dashboard.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(styles)(Dashboard);
