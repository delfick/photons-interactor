import { SelectionState } from "../selection/state.js";
import { ShowError } from "../error.js";

import { withStyles } from "@material-ui/core/styles";
import { connect } from "react-redux";

import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import Button from "@material-ui/core/Button";
import Drawer from "@material-ui/core/Drawer";
import List from "@material-ui/core/List";
import Chip from "@material-ui/core/Chip";

const styles = theme => ({
  drawerPaper: {
    position: "relative",
    width: "400px"
  },
  toolbar: theme.mixins.toolbar
});

const Control = connect()(({ dispatch, selection }) =>
  <div>
    <List>
      <Button
        variant="contained"
        color="primary"
        onClick={() => dispatch(SelectionState.SetPower(true))}
      >
        Power On
      </Button>
      <Button
        variant="contained"
        color="primary"
        onClick={() => dispatch(SelectionState.SetPower(false))}
      >
        Power Off
      </Button>
    </List>
    <Divider />
    <List>
      {Object.keys(selection).map(serial =>
        <Chip key={serial} label={serial} />
      )}
    </List>
  </div>
);

const paneconnect = connect((state, ownProps) => ({
  selection: state.selection.selection,
  error: state.selection.error
}));
const Pane = paneconnect(({ classes, error, selection }) =>
  <Drawer variant="permanent" anchor="right" className={classes.drawerPaper}>
    <ShowError error={error} clearer={SelectionState.ClearError()} />
    <div className={classes.toolbar} />
    <div style={{ width: "400px", paddingTop: "10px", paddingLeft: "10px" }}>
      <List>
        <Typography variant="display2">Control</Typography>
        {Object.keys(selection).length == 0
          ? <Typography variant="subheading">
              Click devices to control
            </Typography>
          : <Control selection={selection} />}{" "}
      </List>
    </div>
  </Drawer>
);

export const ControlPane = withStyles(styles)(Pane);
