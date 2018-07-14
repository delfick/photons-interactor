import { connect } from "react-redux";

import IconButton from "@material-ui/core/IconButton";
import Snackbar from "@material-ui/core/Snackbar";
import CloseIcon from "@material-ui/icons/Close";

export const ShowError = connect()(({ dispatch, error, clearer }) =>
  <Snackbar
    anchorOrigin={{
      vertical: "bottom",
      horizontal: "left"
    }}
    open={error !== undefined}
    onClose={() => dispatch(clearer)}
    autoHideDuration={5000}
    ContentProps={{
      "aria-describedby": "message-id"
    }}
    action={[
      <IconButton
        key="close"
        aria-label="Close"
        color="inherit"
        onClick={() => dispatch(clearer)}
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
);
