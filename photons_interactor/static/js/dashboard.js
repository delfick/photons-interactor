import React from "react";
import PropTypes from "prop-types";
import { withStyles } from "@material-ui/core/styles";
import Grid from "@material-ui/core/Grid";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import CircularProgress from "@material-ui/core/CircularProgress";
import { connect } from "react-redux";
import Snackbar from "@material-ui/core/Snackbar";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";

import { DevicesState } from "./devices.js";

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

var dashconnector = connect((state, ownProps) => ({
  error: state.devices.error,
  serials: state.devices.serials,
  loading: state.devices.loading
}));
const Dashboard = dashconnector(
  ({ error, loading, serials, width, classes, spacing, dispatch }) =>
    <div>
      <Typography variant="display2">Devices</Typography>
      {error
        ? <Snackbar
            anchorOrigin={{
              vertical: "bottom",
              horizontal: "left"
            }}
            open={error !== undefined}
            onClose={() => dispatch(DevicesState.ClearError())}
            autoHideDuration={6000}
            ContentProps={{
              "aria-describedby": "message-id"
            }}
            action={[
              <IconButton
                key="close"
                aria-label="Close"
                color="inherit"
                className={classes.close}
                onClick={() => dispatch(DevicesState.ClearError())}
              >
                <CloseIcon />
              </IconButton>
            ]}
            message={
              <span id="message-id">
                {error}
              </span>
            }
          />
        : null}

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
