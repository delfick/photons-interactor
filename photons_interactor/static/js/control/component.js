import { SelectionState } from "../selection/state.js";
import { ColourPicker } from "../wheel/wheel.js";
import { ControlState } from "./state.js";
import { ShowError } from "../error.js";

import { withStyles } from "@material-ui/core/styles";
import { throttle } from "throttle-debounce";
import { connect } from "react-redux";

import CircularProgress from "@material-ui/core/CircularProgress";
import Typography from "@material-ui/core/Typography";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";
import Divider from "@material-ui/core/Divider";
import Button from "@material-ui/core/Button";
import Drawer from "@material-ui/core/Drawer";
import Hidden from "@material-ui/core/Hidden";
import List from "@material-ui/core/List";
import Chip from "@material-ui/core/Chip";

const styles = theme => ({
  drawerPaper: {
    position: "relative",
    width: "400px"
  },
  controlClose: {
    float: "right"
  },
  toolbar: theme.mixins.toolbar
});

const Control = connect((state, ownProps) => ({
  light_state: state.selection.light_state,
  waiting: state.selection.waiting,
  white: state.selection.white
}))(({ dispatch, selection, light_state, white, waiting }) => (
  <div>
    {waiting ? (
      <CircularProgress size={100} />
    ) : (
      <div>
        <List style={{ marginLeft: "109px" }}>
          <Button
            variant="contained"
            color="primary"
            disabled={!white}
            onClick={() => dispatch(SelectionState.ToggleWheel(false))}
          >
            Color
          </Button>
          <Button
            variant="contained"
            color="primary"
            disabled={white}
            onClick={() => dispatch(SelectionState.ToggleWheel(true))}
          >
            White
          </Button>
        </List>
        <List>
          <ColourPicker
            style={{ marginLeft: "50px" }}
            white={white}
            on={light_state.on}
            hue={light_state.hue}
            width={300}
            height={300}
            brightness={light_state.brightness}
            saturation={light_state.saturation}
            kelvin={light_state.kelvin}
            submit={throttle(300, false, (transform, components) =>
              dispatch(SelectionState.ChangeState(transform, components))
            )}
          />
        </List>
      </div>
    )}
    <Divider />
    <List>
      {Object.keys(selection).map(serial => (
        <Chip key={serial} label={serial} />
      ))}
    </List>
  </div>
));

const ControlContents = connect()(
  ({ selection, closer, classes, dispatch }) => (
    <div style={{ width: "400px", paddingTop: "10px", paddingLeft: "10px" }}>
      <List>
        {closer ? (
          <IconButton
            className={classes.controlClose}
            color="inherit"
            aria-label="Control"
            onClick={e => dispatch(ControlState.Close())}
          >
            <CloseIcon />
          </IconButton>
        ) : null}
        <Typography variant="display2">Control</Typography>
        {Object.keys(selection).length == 0 ? (
          <Typography variant="subheading">Click devices to control</Typography>
        ) : (
          <Control selection={selection} />
        )}{" "}
      </List>
    </div>
  )
);

const Pane = connect((state, ownProps) => ({
  selection: state.selection.selection,
  error: state.selection.error,
  open: state.control.open
}))(({ classes, error, selection, open, dispatch }) => (
  <div>
    <Hidden smUp implementation="css">
      <Drawer
        variant="temporary"
        anchor="right"
        className={classes.drawerPaper}
        open={open}
        onClose={e => dispatch(ControlState.Close())}
      >
        <ShowError error={error} clearer={SelectionState.ClearError()} />
        <ControlContents
          selection={selection}
          closer={true}
          classes={classes}
        />
      </Drawer>
    </Hidden>
    <Hidden smDown implementation="css">
      <Drawer
        variant="permanent"
        anchor="right"
        className={classes.drawerPaper}
        open={open}
        onClose={e => dispatch(ControlState.Close())}
      >
        <ShowError error={error} clearer={SelectionState.ClearError()} />
        <div className={classes.toolbar} />
        <ControlContents selection={selection} />
      </Drawer>
    </Hidden>
  </div>
));

export const ControlPane = withStyles(styles)(Pane);
