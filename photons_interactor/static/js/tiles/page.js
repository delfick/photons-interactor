import { DevicesState } from "../device/state.js";
import { AnimationsState } from "./state.js";
import { ShowError } from "../error.js";

import { connect } from "react-redux";
import PropTypes from "prop-types";
import React from "react";

import CircularProgress from "@material-ui/core/CircularProgress";
import PauseIcon from "@material-ui/icons/PauseCircleFilled";
import PlayIcon from "@material-ui/icons/PlayCircleFilled";
import CardContent from "@material-ui/core/CardContent";
import { withStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import RefreshIcon from "@material-ui/icons/Refresh";
import CancelIcon from "@material-ui/icons/Cancel";
import MenuItem from "@material-ui/core/MenuItem";
import Toolbar from "@material-ui/core/Toolbar";
import Divider from "@material-ui/core/Divider";
import Select from "@material-ui/core/Select";
import AppBar from "@material-ui/core/AppBar";
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import Card from "@material-ui/core/Card";

const styles = theme => ({
  devices: {
    flexGrow: 1,
    marginTop: "10px"
  },
  bar: { flexGrow: 1 },
  devicesTitle: {
    borderRight: "0.1em solid black",
    padding: "8px 16px 8px 0px"
  },
  tilecard: {
    minWidth: 275
  },
  tilecardtitle: {
    fontSize: 14
  },
  tileitem: {
    paddingLeft: "1%!important",
    paddingRight: "1%!important"
  },
  animationControl: {
    paddingLeft: "10px",
    minWidth: 0
  }
});

function summary(info) {
  if (info.running) {
    return "Running";
  } else {
    return "Finished";
  }
}

function animation_buttons(info) {
  if (!info.running) {
    return [];
  }

  var final = [];
  if (info.paused) {
    final.push([<PlayIcon />, AnimationsState.ResumeAnimation]);
  } else {
    final.push([<PauseIcon />, AnimationsState.PauseAnimation]);
  }

  return final;
}

const Animation = withStyles(styles)(
  connect()(({ dispatch, animation_id, info, classes }) => (
    <Grid container direction="row" justify="flex-start" alignItems="center">
      <Grid item>
        <Button
          onClick={e => dispatch(AnimationsState.RemoveAnimation(animation_id))}
          className={classes.animationControl}
        >
          <CancelIcon />
        </Button>
      </Grid>
      {animation_buttons(info).map(([icon, action], i) => (
        <Grid item key={i}>
          <Button
            className={classes.animationControl}
            onClick={e => dispatch(action(animation_id))}
          >
            {icon}
          </Button>
        </Grid>
      ))}
      <Grid item>
        <Typography color="inherit">
          {info.name} | {summary(info)}
        </Typography>
      </Grid>
    </Grid>
  ))
);

@withStyles(styles)
@connect((state, ownProps) => ({ available: state.animations.available }))
class StartAnimationChooser extends React.Component {
  state = { chosen: undefined };

  chosen(available) {
    if (this.state.chosen === undefined) {
      return available[0];
    }
    return this.state.chosen;
  }

  render() {
    var { dispatch, serial, available, classes } = this.props;

    return (
      <div>
        <Button
          onClick={e =>
            dispatch(
              AnimationsState.StartAnimation({ serial }, this.chosen(available))
            )
          }
          className={classes.animationControl}
        >
          <PlayIcon />
        </Button>

        <Select
          value={this.chosen(available)}
          onChange={e => this.setState({ chosen: e.target.value })}
        >
          {available.map(name => (
            <MenuItem key={name} value={name}>
              {name}
            </MenuItem>
          ))}
        </Select>
      </div>
    );
  }
}

const TilesBar = withStyles(styles)(
  connect((state, ownProps) => ({}))(({ classes, dispatch }) => (
    <div className={classes.bar}>
      <AppBar position="static" color="default">
        <Toolbar>
          <Typography
            className={classes.devicesTitle}
            variant="h6"
            color="inherit"
          >
            Tiles
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

function no_running_animation(animations) {
  let no_running_animation = true;
  animations.map(({ info }) => {
    if (info.running) {
      no_running_animation = false;
    }
  });
  return no_running_animation;
}

function tiles_from(serials, devices, statuses) {
  var labels = {};
  var animationInfos = {};

  serials.map(serial => {
    if (
      devices &&
      devices[serial] &&
      devices[serial].cap &&
      devices[serial].cap.includes("chain")
    ) {
      labels[serial] = devices[serial].label;
    }
  });

  Object.keys(statuses).map(animation_id => {
    var info = statuses[animation_id];
    info.serials.map(serial => {
      if (animationInfos[serial] === undefined) {
        animationInfos[serial] = { label: labels[serial], animations: [] };
      }
      animationInfos[serial].animations.push({ info, animation_id });
    });
  });

  Object.keys(labels).map(serial => {
    if (!animationInfos[serial]) {
      animationInfos[serial] = { label: labels[serial], animations: [] };
    }
  });

  var final = [];
  Object.keys(animationInfos)
    .sort()
    .map(serial => {
      var animations = animationInfos[serial].animations.sort(
        (a, b) => b.info.started - a.info.started
      );
      var title = serial;
      if (animationInfos[serial].label) {
        title = title + " - " + animationInfos[serial].label;
      }
      final.push([serial, title, animations]);
    });

  return final;
}

var dashconnector = connect((state, ownProps) => ({
  error: state.devices.error,
  serials: state.devices.serials,
  devices: state.devices.devices,
  loading: state.devices.loading,
  statuses: state.animations.statuses
}));
export const TilesPage = withStyles(styles)(
  dashconnector(
    ({ error, loading, serials, devices, statuses, classes, dispatch }) => (
      <div>
        <TilesBar />
        <ShowError error={error} clearer={DevicesState.ClearError()} />
        <Grid container className={classes.devices} spacing={16}>
          <Grid item xs={12}>
            <Grid
              container
              className={classes.demo}
              justify="center"
              spacing={16}
              direction="column"
              alignItems="stretch"
            >
              {loading ? <CircularProgress /> : null}
              {tiles_from(serials, devices, statuses).map(
                ([serial, title, animations]) => (
                  <Grid key={serial} item className={classes.tileitem}>
                    <Card className={classes.tilecard}>
                      <CardContent>
                        <Typography
                          className={classes.tilecardtitle}
                          color="textSecondary"
                          gutterBottom
                        >
                          {title}
                        </Typography>
                        <Grid
                          container
                          direction="column"
                          justify="center"
                          alignItems="flex-start"
                        >
                          {no_running_animation(animations) ? (
                            <Grid item>
                              <StartAnimationChooser serial={serial} />
                            </Grid>
                          ) : null}
                          {animations.map(info => (
                            <Grid item key={info.animation_id}>
                              <Animation
                                info={info.info}
                                animation_id={info.animation_id}
                              />
                            </Grid>
                          ))}
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>
                )
              )}
            </Grid>
          </Grid>
        </Grid>
      </div>
    )
  )
);
