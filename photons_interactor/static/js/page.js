import { ControlPane } from "./control/component.js";
import { ControlState } from "./control/state.js";

import { connect } from "react-redux";
import PropTypes from "prop-types";
import React from "react";

import { withStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import IconButton from "@material-ui/core/IconButton";
import withWidth from "@material-ui/core/withWidth";
import Toolbar from "@material-ui/core/Toolbar";
import EditIcon from "@material-ui/icons/Edit";
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
  grow: { flexGrow: 1 },
  menuButton: {
    marginLeft: -12
  },
  toolbar: theme.mixins.toolbar,
  appBar: {
    zIndex: theme.zIndex.drawer + 1
  }
});

const Page = connect()(({ width, children, classes, dispatch }) => (
  <div>
    <div className={classes.root}>
      <AppBar position="absolute" className={classes.appBar}>
        <Toolbar>
          <Typography
            variant="title"
            color="inherit"
            className={classes.grow}
            noWrap
          >
            Interactor
          </Typography>
          <Hidden mdUp implementation="css">
            <IconButton
              className={classes.menuButton}
              color="inherit"
              aria-label="Control"
              onClick={e => dispatch(ControlState.Toggle())}
            >
              <EditIcon />
            </IconButton>
          </Hidden>
        </Toolbar>
      </AppBar>
      <main className={classes.content}>
        <div className={classes.toolbar} />
        {children}
      </main>
      <ControlPane />
    </div>
  </div>
));

Page.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withWidth()(withStyles(styles)(Page));
