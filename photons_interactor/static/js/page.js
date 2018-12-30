import { ControlPane } from "./control/component.js";
import { ControlState } from "./control/state.js";
import { ChangePath } from "./router.js";

import { connect } from "react-redux";
import { Route } from "react-router";
import PropTypes from "prop-types";
import React from "react";

import VideoLibraryIcon from "@material-ui/icons/VideoLibrary";
import DashboardIcon from "@material-ui/icons/Dashboard";
import { withStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import IconButton from "@material-ui/core/IconButton";
import withWidth from "@material-ui/core/withWidth";
import Toolbar from "@material-ui/core/Toolbar";
import EditIcon from "@material-ui/icons/Edit";
import Button from "@material-ui/core/Button";
import Hidden from "@material-ui/core/Hidden";
import AppBar from "@material-ui/core/AppBar";
import Grid from "@material-ui/core/Grid";

const styles = theme => ({
  root: {
    flexGrow: 1,
    height: 430,
    zIndex: 1,
    overflow: "hidden",
    position: "relative",
    display: "flex",
    height: "100vh"
  },
  content: {
    flexGrow: 1,
    height: "100vh",
    backgroundColor: theme.palette.background.default,
    padding: theme.spacing.unit * 3,
    minWidth: 0 // So the Typography noWrap works
  },
  menuButton: {
    marginLeft: -12,
    float: "right"
  },
  toolbar: theme.mixins.toolbar,
  appBar: {
    zIndex: theme.zIndex.drawer + 1
  },
  navButton: {
    marginLeft: theme.spacing.unit * 2,
    margin: theme.spacing.unit
  },
  navLeftIcon: {
    marginRight: theme.spacing.unit
  },
  toolbarRightButtons: {
    marginLeft: "auto",
    marginRight: -12
  }
});

const GoToTilesButton = connect()(({ classes, dispatch }) => (
  <Button
    variant="contained"
    color="default"
    className={classes.navButton}
    href="/tiles"
    onClick={e => {
      e.preventDefault();
      dispatch(ChangePath("/tiles"));
    }}
  >
    <VideoLibraryIcon className={classes.navLeftIcon} />
    Tiles
  </Button>
));

const GoToHomeButton = connect()(({ classes, dispatch }) => (
  <Button
    variant="contained"
    color="default"
    className={classes.navButton}
    href="/tiles"
    onClick={e => {
      e.preventDefault();
      dispatch(ChangePath("/"));
    }}
  >
    <DashboardIcon className={classes.navLeftIcon} />
    Home
  </Button>
));

const OpenControlPaneButton = connect()(({ classes, dispatch }) => (
  <Hidden mdUp implementation="css" className={classes.toolbarRightButtons}>
    <IconButton
      className={classes.menuButton}
      color="inherit"
      aria-label="Control"
      onClick={e => dispatch(ControlState.Toggle())}
    >
      <EditIcon />
    </IconButton>
  </Hidden>
));

const Page = ({ width, children, classes }) => (
  <div>
    <div className={classes.root}>
      <AppBar position="absolute" className={classes.appBar}>
        <Toolbar>
          <Typography variant="h6" color="inherit" noWrap>
            Interactor
          </Typography>
          {window.location.pathname === "/" ? (
            <GoToTilesButton classes={classes} />
          ) : (
            <GoToHomeButton classes={classes} />
          )}
          {window.location.pathname === "/" ? (
            <OpenControlPaneButton classes={classes} />
          ) : null}
        </Toolbar>
      </AppBar>
      <main className={classes.content}>
        <div className={classes.toolbar} />
        {children}
      </main>
      {window.location.pathname === "/" ? <ControlPane /> : null}
    </div>
  </div>
);

Page.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withWidth()(withStyles(styles)(Page));
