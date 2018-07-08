import React from "react";
import PropTypes from "prop-types";
import withWidth from "@material-ui/core/withWidth";
import { withStyles } from "@material-ui/core/styles";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Grid from "@material-ui/core/Grid";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";

const styles = {
  root: {
    flexGrow: 1
  },
  flex: {
    flex: 1
  },
  menuButton: {
    marginLeft: -12,
    marginRight: 20
  }
};

const Page = ({ width, children, classes }) => {
  var padding = {
    xs: "10px",
    sm: "20px",
    md: "30px",
    lg: "50px",
    xl: "80px"
  };

  var rootStyle = {
    marginTop: "80px",
    marginBottom: "15px",
    paddingLeft: padding[width] || "80px",
    paddingRight: padding[width] || "80px"
  };

  return (
    <div>
      <div className={classes.root}>
        <AppBar>
          <Toolbar>
            <IconButton
              className={classes.menuButton}
              color="inherit"
              aria-label="Menu"
            >
              <MenuIcon />
            </IconButton>
            <Typography
              variant="title"
              color="inherit"
              className={classes.flex}
            >
              Interactor
            </Typography>
          </Toolbar>
        </AppBar>
        <Grid container style={rootStyle}>
          {children}
        </Grid>
      </div>
    </div>
  );
};

Page.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withWidth()(withStyles(styles)(Page));
