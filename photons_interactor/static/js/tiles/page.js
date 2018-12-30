import { AnimationsState, DisplayDice, TilesState } from "./state.js";
import { DevicesState } from "../device/state.js";
import { TilesArranger } from "./arrange.js";
import { ChangePath } from "../router.js";
import { ShowError } from "../error.js";
import { history } from "../history.js";

import { Router, Route, Switch } from "react-router";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import React from "react";

import CircularProgress from "@material-ui/core/CircularProgress";
import ArrowDropDownIcon from "@material-ui/icons/ArrowDropDown";
import MuiDialogContent from "@material-ui/core/DialogContent";
import MuiDialogActions from "@material-ui/core/DialogActions";
import PauseIcon from "@material-ui/icons/PauseCircleFilled";
import PlayIcon from "@material-ui/icons/PlayCircleFilled";
import MuiDialogTitle from "@material-ui/core/DialogTitle";
import CardContent from "@material-ui/core/CardContent";
import MoreVertIcon from "@material-ui/icons/MoreVert";
import { withStyles } from "@material-ui/core/styles";
import CardHeader from "@material-ui/core/CardHeader";
import Typography from "@material-ui/core/Typography";
import IconButton from "@material-ui/core/IconButton";
import RefreshIcon from "@material-ui/icons/Refresh";
import CancelIcon from "@material-ui/icons/Cancel";
import MenuItem from "@material-ui/core/MenuItem";
import CloseIcon from "@material-ui/icons/Close";
import Toolbar from "@material-ui/core/Toolbar";
import Dialog from "@material-ui/core/Dialog";
import Select from "@material-ui/core/Select";
import AppBar from "@material-ui/core/AppBar";
import Button from "@material-ui/core/Button";
import Menu from "@material-ui/core/Menu";
import Grid from "@material-ui/core/Grid";
import Card from "@material-ui/core/Card";
import Chip from "@material-ui/core/Chip";

const styles = theme => ({
  devices: {
    flexGrow: 1,
    marginTop: "10px"
  },
  bar: { flexGrow: 1 },
  tileTitle: {
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
  },
  dialogerror: {
    margin: theme.spacing.unit
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
    var { dispatch, serial, available, classes, combine_tiles } = this.props;

    return (
      <div>
        <Button
          onClick={e =>
            dispatch(
              AnimationsState.StartAnimation(
                { serial },
                this.chosen(available),
                { combine_tiles }
              )
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

@withStyles(styles)
@connect()
class TilePageChanger extends React.Component {
  state = { anchorEl: null };

  handleClick(event) {
    this.setState({ anchorEl: event.currentTarget });
  }

  goTo(path) {
    this.setState({ anchorEl: null });
    this.props.dispatch(ChangePath(path));
  }

  render() {
    const { anchorEl } = this.state;

    return (
      <div>
        <Button
          aria-owns={anchorEl ? "tile-page-menu" : undefined}
          aria-haspopup="true"
          onClick={this.handleClick.bind(this)}
          variant="outlined"
        >
          <Router history={history}>
            <Switch>
              <Route
                exact
                path="/tiles/animate"
                render={() => <span>Animate</span>}
              />
              <Route
                exact
                path="/tiles/arrange"
                render={() => <span>Arrange</span>}
              />
            </Switch>
          </Router>
          <ArrowDropDownIcon />
        </Button>
        <Menu
          id="simple-menu"
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={this.handleClose}
        >
          <MenuItem onClick={this.goTo.bind(this, "/tiles/animate")}>
            Animate
          </MenuItem>
          <MenuItem onClick={this.goTo.bind(this, "/tiles/arrange")}>
            Arrange
          </MenuItem>
        </Menu>
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
            className={classes.tileTitle}
            variant="h6"
            color="inherit"
          >
            Tiles
          </Typography>
          <TilePageChanger />
          <Router history={history}>
            <Switch>
              <Route
                exact
                path="/tiles/animate"
                render={() => (
                  <Button onClick={e => dispatch(DevicesState.Refresh())}>
                    <RefreshIcon />
                  </Button>
                )}
              />
              <Route
                exact
                path="/tiles/arrange"
                render={() => (
                  <Button onClick={e => dispatch(TilesState.StartArrange())}>
                    <RefreshIcon />
                  </Button>
                )}
              />
            </Switch>
          </Router>
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

function no_running_statuses(statuses) {
  let no_running_statuses = true;
  Object.keys(statuses).map(id => {
    var info = statuses[id];
    if (info.running) {
      no_running_statuses = false;
    }
  });
  return no_running_statuses;
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

const DialogTitle = withStyles(theme => ({
  root: {
    borderBottom: `1px solid ${theme.palette.divider}`,
    margin: 0,
    padding: theme.spacing.unit * 2
  },
  closeButton: {
    position: "absolute",
    right: theme.spacing.unit,
    top: theme.spacing.unit,
    color: theme.palette.grey[500]
  }
}))(props => {
  const { children, classes, onClose } = props;
  return (
    <MuiDialogTitle disableTypography className={classes.root}>
      <Typography variant="h6">{children}</Typography>
      <IconButton
        aria-label="Close"
        className={classes.closeButton}
        onClick={onClose}
      >
        <CloseIcon />
      </IconButton>
    </MuiDialogTitle>
  );
});

const DialogContent = withStyles(theme => ({
  root: {
    margin: 0,
    padding: theme.spacing.unit * 2
  }
}))(MuiDialogContent);

@withStyles(styles)
@connect()
class TileOptions extends React.Component {
  state = {
    anchorEl: null,
    dialogopen: false,
    dialogloading: false,
    dialogerror: undefined,
    dialogmade: undefined
  };

  handleClick(event) {
    this.setState({ anchorEl: event.currentTarget });
  }

  handleClose() {
    this.setState({ anchorEl: null });
  }

  onDialogClose() {
    this.setState({ dialogopen: false });
  }

  displayDice(dispatch, serial) {
    this.setState({
      dialogloading: true,
      dialogopen: true,
      dialogerror: undefined,
      dialogmade: undefined
    });
    this.handleClose();
    var onFinish = this.onDoneDice.bind(this);
    dispatch(DisplayDice(serial, onFinish));
  }

  onDoneDice(error, made) {
    this.setState({
      dialogloading: false,
      dialogerror: error,
      dialogmade: made
    });

    if (made && made.length > 0) {
      var canvas = this.refs.tiles;
      var canvasDom = ReactDOM.findDOMNode(canvas);

      var dialog = this.refs.dialog;
      var dialogDom = ReactDOM.findDOMNode(dialog);

      var width = dialogDom.getBoundingClientRect().width - 20;
      canvasDom.width = width;

      var ctx = canvas.getContext("2d");

      ctx.fillStyle = "rgba(0, 0, 1, 0)";
      ctx.fillRect(0, 0, width, 300);

      var cellWidth = Math.floor(width / 5 / 9);

      var drawIndividual = function(i, hsbks) {
        var startx = cellWidth * 9 * i;
        var starty = cellWidth;
        ctx.clearRect(startx, starty, 240, 240);
        for (var j = 0; j < hsbks.length; j++) {
          var row = Math.floor(j / 8);
          var col = j % 8;
          var x = startx + col * cellWidth;
          var y = starty + cellWidth * row;
          ctx.fillStyle = hsbks[j];
          ctx.fillRect(x, y, cellWidth, cellWidth);
        }
      };

      made.map((hsbks, i) => drawIndividual(i, hsbks));
    }
  }

  render() {
    const { anchorEl } = this.state;
    const { serial, dispatch, classes } = this.props;
    const open = Boolean(anchorEl);

    return (
      <div>
        <IconButton
          aria-label="More"
          aria-owns={open ? "tile-menu" : undefined}
          aria-haspopup="true"
          onClick={this.handleClick.bind(this)}
        >
          <MoreVertIcon />
        </IconButton>
        <Menu
          id="tile-menu"
          anchorEl={anchorEl}
          open={open}
          onClose={this.handleClose.bind(this)}
        >
          <MenuItem onClick={() => this.displayDice(dispatch, serial)}>
            Dice
          </MenuItem>
        </Menu>
        <Dialog
          onClose={this.onDialogClose.bind(this)}
          aria-labelledby="applying-dice"
          open={this.state.dialogopen}
          fullWidth={true}
        >
          <DialogTitle onClose={this.onDialogClose.bind(this)}>
            Applying dice
          </DialogTitle>
          {this.state.dialogloading ? (
            <DialogContent>
              <CircularProgress />
            </DialogContent>
          ) : (
            <DialogContent ref="dialog">
              {this.state.dialogerror ? (
                <Chip
                  color="secondary"
                  label={this.state.dialogerror}
                  className={classes.dialogerror}
                  variant="outlined"
                />
              ) : null}
              {this.state.dialogmade && this.state.dialogmade.length > 0 ? (
                <Typography gutterBottom>
                  For horizontal tile animations like tile_time or tile_nyan,
                  it's best that your tiles are arranged to look like the
                  following
                </Typography>
              ) : null}
              {this.state.dialogmade && this.state.dialogmade.length > 0 ? (
                <canvas className={classes.tiledicecanvas} ref="tiles" />
              ) : null}
            </DialogContent>
          )}
        </Dialog>
      </div>
    );
  }
}

export const TilesPage = connect((state, ownProps) => ({
  error: state.devices.error
}))(({ error }) => (
  <div style={{ height: "100%" }}>
    <TilesBar />
    <ShowError error={error} clearer={DevicesState.ClearError()} />
    <Router history={history}>
      <Switch>
        <Route exact path="/tiles/animate" component={AnimationList} />
        <Route
          exact
          path="/tiles/arrange"
          render={() => <TilesArranger style={{ height: "100%" }} />}
        />
      </Switch>
    </Router>
  </div>
));

var dashconnector = connect((state, ownProps) => ({
  error: state.devices.error,
  serials: state.devices.serials,
  devices: state.devices.devices,
  loading: state.devices.loading,
  statuses: state.animations.statuses
}));
export const AnimationList = withStyles(styles)(
  dashconnector(
    ({ error, loading, serials, devices, statuses, classes, dispatch }) => (
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
            {no_running_statuses(statuses) &&
            tiles_from(serials, devices, {}).length > 0 ? (
              <Grid item className={classes.tileitem}>
                <Card className={classes.tilecard}>
                  <CardHeader
                    avatar={<TileOptions serial={serials} />}
                    subheader="ALL TILES"
                  />
                  <CardContent>
                    <StartAnimationChooser
                      serial={serials}
                      combine_tiles={true}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ) : null}
            {tiles_from(serials, devices, statuses).map(
              ([serial, title, animations]) => (
                <Grid key={serial} item className={classes.tileitem}>
                  <Card className={classes.tilecard}>
                    <CardHeader
                      avatar={<TileOptions serial={serial} />}
                      subheader={title}
                    />
                    <CardContent>
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
    )
  )
);
