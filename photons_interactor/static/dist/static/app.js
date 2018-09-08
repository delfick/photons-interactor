/******/ (function(modules) { // webpackBootstrap
/******/ 	// install a JSONP callback for chunk loading
/******/ 	function webpackJsonpCallback(data) {
/******/ 		var chunkIds = data[0];
/******/ 		var moreModules = data[1];
/******/ 		var executeModules = data[2];
/******/
/******/ 		// add "moreModules" to the modules object,
/******/ 		// then flag all "chunkIds" as loaded and fire callback
/******/ 		var moduleId, chunkId, i = 0, resolves = [];
/******/ 		for(;i < chunkIds.length; i++) {
/******/ 			chunkId = chunkIds[i];
/******/ 			if(installedChunks[chunkId]) {
/******/ 				resolves.push(installedChunks[chunkId][0]);
/******/ 			}
/******/ 			installedChunks[chunkId] = 0;
/******/ 		}
/******/ 		for(moduleId in moreModules) {
/******/ 			if(Object.prototype.hasOwnProperty.call(moreModules, moduleId)) {
/******/ 				modules[moduleId] = moreModules[moduleId];
/******/ 			}
/******/ 		}
/******/ 		if(parentJsonpFunction) parentJsonpFunction(data);
/******/
/******/ 		while(resolves.length) {
/******/ 			resolves.shift()();
/******/ 		}
/******/
/******/ 		// add entry modules from loaded chunk to deferred list
/******/ 		deferredModules.push.apply(deferredModules, executeModules || []);
/******/
/******/ 		// run deferred modules when all chunks ready
/******/ 		return checkDeferredModules();
/******/ 	};
/******/ 	function checkDeferredModules() {
/******/ 		var result;
/******/ 		for(var i = 0; i < deferredModules.length; i++) {
/******/ 			var deferredModule = deferredModules[i];
/******/ 			var fulfilled = true;
/******/ 			for(var j = 1; j < deferredModule.length; j++) {
/******/ 				var depId = deferredModule[j];
/******/ 				if(installedChunks[depId] !== 0) fulfilled = false;
/******/ 			}
/******/ 			if(fulfilled) {
/******/ 				deferredModules.splice(i--, 1);
/******/ 				result = __webpack_require__(__webpack_require__.s = deferredModule[0]);
/******/ 			}
/******/ 		}
/******/ 		return result;
/******/ 	}
/******/
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// object to store loaded and loading chunks
/******/ 	// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 	// Promise = chunk loading, 0 = chunk loaded
/******/ 	var installedChunks = {
/******/ 		"main": 0
/******/ 	};
/******/
/******/ 	var deferredModules = [];
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	var jsonpArray = window["webpackJsonp"] = window["webpackJsonp"] || [];
/******/ 	var oldJsonpFunction = jsonpArray.push.bind(jsonpArray);
/******/ 	jsonpArray.push = webpackJsonpCallback;
/******/ 	jsonpArray = jsonpArray.slice();
/******/ 	for(var i = 0; i < jsonpArray.length; i++) webpackJsonpCallback(jsonpArray[i]);
/******/ 	var parentJsonpFunction = oldJsonpFunction;
/******/
/******/
/******/ 	// add entry module to deferred list
/******/ 	deferredModules.push([0,"vendor"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./css/app.scss":
/*!**********************!*\
  !*** ./css/app.scss ***!
  \**********************/
/*! no static exports found */
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "./js/control/component.js":
/*!*********************************!*\
  !*** ./js/control/component.js ***!
  \*********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function(React) {

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ControlPane = undefined;

var _state = __webpack_require__(/*! ../selection/state.js */ "./js/selection/state.js");

var _wheel = __webpack_require__(/*! ../wheel/wheel.js */ "./js/wheel/wheel.js");

var _error = __webpack_require__(/*! ../error.js */ "./js/error.js");

var _styles = __webpack_require__(/*! @material-ui/core/styles */ "./node_modules/@material-ui/core/styles/index.js");

var _throttleDebounce = __webpack_require__(/*! throttle-debounce */ "./node_modules/throttle-debounce/index.esm.js");

var _reactRedux = __webpack_require__(/*! react-redux */ "./node_modules/react-redux/es/index.js");

var _CircularProgress = __webpack_require__(/*! @material-ui/core/CircularProgress */ "./node_modules/@material-ui/core/CircularProgress/index.js");

var _CircularProgress2 = _interopRequireDefault(_CircularProgress);

var _Typography = __webpack_require__(/*! @material-ui/core/Typography */ "./node_modules/@material-ui/core/Typography/index.js");

var _Typography2 = _interopRequireDefault(_Typography);

var _Divider = __webpack_require__(/*! @material-ui/core/Divider */ "./node_modules/@material-ui/core/Divider/index.js");

var _Divider2 = _interopRequireDefault(_Divider);

var _Button = __webpack_require__(/*! @material-ui/core/Button */ "./node_modules/@material-ui/core/Button/index.js");

var _Button2 = _interopRequireDefault(_Button);

var _Drawer = __webpack_require__(/*! @material-ui/core/Drawer */ "./node_modules/@material-ui/core/Drawer/index.js");

var _Drawer2 = _interopRequireDefault(_Drawer);

var _List = __webpack_require__(/*! @material-ui/core/List */ "./node_modules/@material-ui/core/List/index.js");

var _List2 = _interopRequireDefault(_List);

var _Chip = __webpack_require__(/*! @material-ui/core/Chip */ "./node_modules/@material-ui/core/Chip/index.js");

var _Chip2 = _interopRequireDefault(_Chip);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var styles = function styles(theme) {
  return {
    drawerPaper: {
      position: "relative",
      width: "400px"
    },
    toolbar: theme.mixins.toolbar
  };
};

var Control = (0, _reactRedux.connect)(function (state, ownProps) {
  return {
    light_state: state.selection.light_state,
    waiting: state.selection.waiting,
    white: state.selection.white
  };
})(function (_ref) {
  var dispatch = _ref.dispatch,
      selection = _ref.selection,
      light_state = _ref.light_state,
      white = _ref.white,
      waiting = _ref.waiting;
  return React.createElement(
    "div",
    null,
    waiting ? React.createElement(_CircularProgress2.default, { size: 100 }) : React.createElement(
      "div",
      null,
      React.createElement(
        _List2.default,
        { style: { marginLeft: "109px" } },
        React.createElement(
          _Button2.default,
          {
            variant: "contained",
            color: "primary",
            disabled: !white,
            onClick: function onClick() {
              return dispatch(_state.SelectionState.ToggleWheel(false));
            }
          },
          "Color"
        ),
        React.createElement(
          _Button2.default,
          {
            variant: "contained",
            color: "primary",
            disabled: white,
            onClick: function onClick() {
              return dispatch(_state.SelectionState.ToggleWheel(true));
            }
          },
          "White"
        )
      ),
      React.createElement(
        _List2.default,
        null,
        React.createElement(_wheel.ColourPicker, {
          style: { marginLeft: "50px" },
          white: white,
          on: light_state.on,
          hue: light_state.hue,
          width: 300,
          height: 300,
          brightness: light_state.brightness,
          saturation: light_state.saturation,
          kelvin: light_state.kelvin,
          submit: (0, _throttleDebounce.throttle)(300, false, function (transform, components) {
            return dispatch(_state.SelectionState.ChangeState(transform, components));
          })
        })
      )
    ),
    React.createElement(_Divider2.default, null),
    React.createElement(
      _List2.default,
      null,
      Object.keys(selection).map(function (serial) {
        return React.createElement(_Chip2.default, { key: serial, label: serial });
      })
    )
  );
});

var paneconnect = (0, _reactRedux.connect)(function (state, ownProps) {
  return {
    selection: state.selection.selection,
    error: state.selection.error
  };
});
var Pane = paneconnect(function (_ref2) {
  var classes = _ref2.classes,
      error = _ref2.error,
      selection = _ref2.selection;
  return React.createElement(
    _Drawer2.default,
    { variant: "permanent", anchor: "right", className: classes.drawerPaper },
    React.createElement(_error.ShowError, { error: error, clearer: _state.SelectionState.ClearError() }),
    React.createElement("div", { className: classes.toolbar }),
    React.createElement(
      "div",
      { style: { width: "400px", paddingTop: "10px", paddingLeft: "10px" } },
      React.createElement(
        _List2.default,
        null,
        React.createElement(
          _Typography2.default,
          { variant: "display2" },
          "Control"
        ),
        Object.keys(selection).length == 0 ? React.createElement(
          _Typography2.default,
          { variant: "subheading" },
          "Click devices to control"
        ) : React.createElement(Control, { selection: selection }),
        " "
      )
    )
  );
});

var ControlPane = exports.ControlPane = (0, _styles.withStyles)(styles)(Pane);
/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! react */ "./node_modules/react/index.js")))

/***/ }),

/***/ "./js/dashboard.js":
/*!*************************!*\
  !*** ./js/dashboard.js ***!
  \*************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _state = __webpack_require__(/*! ./device/state.js */ "./js/device/state.js");

var _component = __webpack_require__(/*! ./device/component.js */ "./js/device/component.js");

var _error = __webpack_require__(/*! ./error.js */ "./js/error.js");

var _reactRedux = __webpack_require__(/*! react-redux */ "./node_modules/react-redux/es/index.js");

var _propTypes = __webpack_require__(/*! prop-types */ "./node_modules/prop-types/index.js");

var _propTypes2 = _interopRequireDefault(_propTypes);

var _react = __webpack_require__(/*! react */ "./node_modules/react/index.js");

var _react2 = _interopRequireDefault(_react);

var _CircularProgress = __webpack_require__(/*! @material-ui/core/CircularProgress */ "./node_modules/@material-ui/core/CircularProgress/index.js");

var _CircularProgress2 = _interopRequireDefault(_CircularProgress);

var _styles = __webpack_require__(/*! @material-ui/core/styles */ "./node_modules/@material-ui/core/styles/index.js");

var _Typography = __webpack_require__(/*! @material-ui/core/Typography */ "./node_modules/@material-ui/core/Typography/index.js");

var _Typography2 = _interopRequireDefault(_Typography);

var _Grid = __webpack_require__(/*! @material-ui/core/Grid */ "./node_modules/@material-ui/core/Grid/index.js");

var _Grid2 = _interopRequireDefault(_Grid);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var styles = function styles(theme) {
  return {
    devices: {
      flexGrow: 1,
      marginTop: "10px"
    }
  };
};

var dashconnector = (0, _reactRedux.connect)(function (state, ownProps) {
  return {
    error: state.devices.error,
    serials: state.devices.serials,
    loading: state.devices.loading
  };
});
var Dashboard = dashconnector(function (_ref) {
  var error = _ref.error,
      loading = _ref.loading,
      serials = _ref.serials,
      width = _ref.width,
      classes = _ref.classes,
      spacing = _ref.spacing,
      dispatch = _ref.dispatch;
  return _react2.default.createElement(
    "div",
    null,
    _react2.default.createElement(
      _Typography2.default,
      { variant: "display2" },
      "Devices"
    ),
    _react2.default.createElement(_error.ShowError, { error: error, clearer: _state.DevicesState.ClearError() }),
    _react2.default.createElement(
      _Grid2.default,
      { container: true, className: classes.devices, spacing: 16 },
      _react2.default.createElement(
        _Grid2.default,
        { item: true, xs: 12 },
        _react2.default.createElement(
          _Grid2.default,
          {
            container: true,
            className: classes.demo,
            justify: "center",
            spacing: 16
          },
          loading ? _react2.default.createElement(_CircularProgress2.default, null) : null,
          serials.map(function (serial) {
            return _react2.default.createElement(
              _Grid2.default,
              { key: serial, item: true },
              _react2.default.createElement(_component.Bulb, { serial: serial })
            );
          })
        )
      )
    )
  );
});

Dashboard.propTypes = {
  classes: _propTypes2.default.object.isRequired
};

exports.default = (0, _styles.withStyles)(styles)(Dashboard);

/***/ }),

/***/ "./js/device/component.js":
/*!********************************!*\
  !*** ./js/device/component.js ***!
  \********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function(React) {

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.Bulb = undefined;

var _state = __webpack_require__(/*! ../selection/state.js */ "./js/selection/state.js");

var _reactRedux = __webpack_require__(/*! react-redux */ "./node_modules/react-redux/es/index.js");

var _CircularProgress = __webpack_require__(/*! @material-ui/core/CircularProgress */ "./node_modules/@material-ui/core/CircularProgress/index.js");

var _CircularProgress2 = _interopRequireDefault(_CircularProgress);

var _CardContent = __webpack_require__(/*! @material-ui/core/CardContent */ "./node_modules/@material-ui/core/CardContent/index.js");

var _CardContent2 = _interopRequireDefault(_CardContent);

var _Typography = __webpack_require__(/*! @material-ui/core/Typography */ "./node_modules/@material-ui/core/Typography/index.js");

var _Typography2 = _interopRequireDefault(_Typography);

var _Card = __webpack_require__(/*! @material-ui/core/Card */ "./node_modules/@material-ui/core/Card/index.js");

var _Card2 = _interopRequireDefault(_Card);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var styles = function styles(theme) {
  return {
    devices: {
      flexGrow: 1,
      marginTop: "10px"
    }
  };
};

var bulbconnector = (0, _reactRedux.connect)(function (state, ownProps) {
  return {
    data: state.devices.devices[ownProps.serial],
    selected: state.selection.selection[ownProps.serial]
  };
});
var Bulb = bulbconnector(function (_ref) {
  var dispatch = _ref.dispatch,
      serial = _ref.serial,
      data = _ref.data,
      selected = _ref.selected;
  return React.createElement(
    _Card2.default,
    {
      "data-cy": "bulb",
      style: selected ? { backgroundColor: "#0000ff14" } : undefined,
      onClick: function onClick() {
        dispatch(_state.SelectionState.ToggleSelection({ serial: serial }));
      }
    },
    React.createElement(
      _CardContent2.default,
      null,
      React.createElement(
        _Typography2.default,
        { component: "p" },
        serial
      ),
      !data ? React.createElement(_CircularProgress2.default, { size: 20 }) : React.createElement(BulbData, { serial: serial, data: data })
    )
  );
});

var BulbData = function BulbData(_ref2) {
  var serial = _ref2.serial,
      data = _ref2.data;
  return React.createElement(
    _Typography2.default,
    { component: "p", "data-cy": "bulb-label" },
    data.label
  );
};

exports.Bulb = Bulb;
/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! react */ "./node_modules/react/index.js")))

/***/ }),

/***/ "./js/device/state.js":
/*!****************************!*\
  !*** ./js/device/state.js ***!
  \****************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.fortests = exports.DevicesState = undefined;

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

exports.deviceSaga = deviceSaga;

var _wsclient = __webpack_require__(/*! ../wsclient.js */ "./js/wsclient.js");

var _effects = __webpack_require__(/*! redux-saga/effects */ "./node_modules/redux-saga/es/effects.js");

var _reduxAct = __webpack_require__(/*! redux-act */ "./node_modules/redux-act/lib/index.js");

var _marked = /*#__PURE__*/regeneratorRuntime.mark(getDetailsSaga),
    _marked2 = /*#__PURE__*/regeneratorRuntime.mark(getSerialsSaga),
    _marked3 = /*#__PURE__*/regeneratorRuntime.mark(deviceSaga);

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var DevicesStateKls = function () {
  function DevicesStateKls() {
    _classCallCheck(this, DevicesStateKls);

    this.GetSerials = (0, _reduxAct.createAction)("Get serials", function (refresh, other_args) {
      return {
        args: _extends({}, other_args, { just_serials: true, refresh: refresh || false })
      };
    });
    this.GotSerials = (0, _reduxAct.createAction)("Got serials");
    this.GetDetails = (0, _reduxAct.createAction)("Get details", function (refresh, other_args) {
      return {
        args: _extends({}, other_args, { refresh: refresh || false })
      };
    });
    this.GotDetails = (0, _reduxAct.createAction)("Got details");
    this.DetailsError = (0, _reduxAct.createAction)("Error getting information");
    this.ClearError = (0, _reduxAct.createAction)("Clear the error");
  }

  _createClass(DevicesStateKls, [{
    key: "reducer",
    value: function reducer() {
      var _createReducer;

      return (0, _reduxAct.createReducer)((_createReducer = {}, _defineProperty(_createReducer, this.GotSerials, function (state, _ref) {
        var serials = _ref.serials;

        return _extends({}, state, { serials: serials, loading: false });
      }), _defineProperty(_createReducer, this.GotDetails, function (state, _ref2) {
        var devices = _ref2.devices;

        return _extends({}, state, {
          devices: devices || {},
          loading: false
        });
      }), _defineProperty(_createReducer, this.DetailsError, function (state, _ref3) {
        var error = _ref3.error;

        var errormsg = error.error_code + ": " + JSON.stringify(error.error);
        return _extends({}, state, { error: errormsg, loading: false });
      }), _defineProperty(_createReducer, this.ClearError, function (state, payload) {
        return _extends({}, state, { error: undefined });
      }), _createReducer), {
        serials: [],
        error: undefined,
        devices: {},
        loading: true
      });
    }
  }]);

  return DevicesStateKls;
}();

var DevicesState = exports.DevicesState = new DevicesStateKls();

function getDetailsSaga(original) {
  var payload, onsuccess, onerror;
  return regeneratorRuntime.wrap(function getDetailsSaga$(_context) {
    while (1) {
      switch (_context.prev = _context.next) {
        case 0:
          payload = original.payload;

          onsuccess = function onsuccess(_ref4) {
            var data = _ref4.data;
            return DevicesState.GotDetails({ devices: data });
          };

          onerror = DevicesState.DetailsError;
          _context.next = 5;
          return (0, _effects.put)((0, _wsclient.WSCommand)("/v1/lifx/command", {
            command: "discover",
            args: payload.args
          }, { onsuccess: onsuccess, onerror: onerror, original: original }));

        case 5:
        case "end":
          return _context.stop();
      }
    }
  }, _marked, this);
}

function getSerialsSaga(original) {
  var payload, onsuccess, onerror;
  return regeneratorRuntime.wrap(function getSerialsSaga$(_context2) {
    while (1) {
      switch (_context2.prev = _context2.next) {
        case 0:
          payload = original.payload;

          onsuccess = function onsuccess(_ref5) {
            var data = _ref5.data;
            return DevicesState.GotSerials({ serials: data });
          };

          onerror = DevicesState.DetailsError;
          _context2.next = 5;
          return (0, _effects.put)((0, _wsclient.WSCommand)("/v1/lifx/command", {
            command: "discover",
            args: _extends({}, payload.args, { just_serials: true })
          }, { onsuccess: onsuccess, onerror: onerror, original: original }));

        case 5:
        case "end":
          return _context2.stop();
      }
    }
  }, _marked2, this);
}

function deviceSaga() {
  return regeneratorRuntime.wrap(function deviceSaga$(_context3) {
    while (1) {
      switch (_context3.prev = _context3.next) {
        case 0:
          _context3.next = 2;
          return (0, _effects.takeLatest)(DevicesState.GetSerials, getSerialsSaga);

        case 2:
          _context3.next = 4;
          return (0, _effects.takeLatest)(DevicesState.GetDetails, getDetailsSaga);

        case 4:
        case "end":
          return _context3.stop();
      }
    }
  }, _marked3, this);
}

var fortests = exports.fortests = { getDetailsSaga: getDetailsSaga, getSerialsSaga: getSerialsSaga };

/***/ }),

/***/ "./js/error.js":
/*!*********************!*\
  !*** ./js/error.js ***!
  \*********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function(React) {

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ShowError = undefined;

var _reactRedux = __webpack_require__(/*! react-redux */ "./node_modules/react-redux/es/index.js");

var _IconButton = __webpack_require__(/*! @material-ui/core/IconButton */ "./node_modules/@material-ui/core/IconButton/index.js");

var _IconButton2 = _interopRequireDefault(_IconButton);

var _Snackbar = __webpack_require__(/*! @material-ui/core/Snackbar */ "./node_modules/@material-ui/core/Snackbar/index.js");

var _Snackbar2 = _interopRequireDefault(_Snackbar);

var _Close = __webpack_require__(/*! @material-ui/icons/Close */ "./node_modules/@material-ui/icons/Close.js");

var _Close2 = _interopRequireDefault(_Close);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var ShowError = exports.ShowError = (0, _reactRedux.connect)()(function (_ref) {
  var dispatch = _ref.dispatch,
      error = _ref.error,
      clearer = _ref.clearer;
  return React.createElement(_Snackbar2.default, {
    anchorOrigin: {
      vertical: "bottom",
      horizontal: "left"
    },
    open: error !== undefined,
    onClose: function onClose() {
      return dispatch(clearer);
    },
    autoHideDuration: 5000,
    ContentProps: {
      "aria-describedby": "message-id"
    },
    action: [React.createElement(
      _IconButton2.default,
      {
        key: "close",
        "aria-label": "Close",
        color: "inherit",
        onClick: function onClick() {
          return dispatch(clearer);
        }
      },
      React.createElement(_Close2.default, null)
    )],
    message: React.createElement(
      "span",
      { id: "message-id" },
      error
    )
  });
});
/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! react */ "./node_modules/react/index.js")))

/***/ }),

/***/ "./js/history.js":
/*!***********************!*\
  !*** ./js/history.js ***!
  \***********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.Link = exports.history = undefined;

var _createBrowserHistory = __webpack_require__(/*! history/createBrowserHistory */ "./node_modules/history/createBrowserHistory.js");

var _createBrowserHistory2 = _interopRequireDefault(_createBrowserHistory);

var _react = __webpack_require__(/*! redux-saga-router/react */ "./node_modules/redux-saga-router/react.js");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var history = exports.history = (0, _createBrowserHistory2.default)();
var Link = exports.Link = (0, _react.createLink)(history);

/***/ }),

/***/ "./js/hsk-to-color.js":
/*!****************************!*\
  !*** ./js/hsk-to-color.js ***!
  \****************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

// Taken from http://stackoverflow.com/a/17243070
exports.default = function (hue, saturation, kelvin) {
  function HSLtoHSV(h, s, l) {
    if (arguments.length === 1) {
      s = h.s, l = h.l, h = h.h;
    }
    var _h = h,
        _s,
        _v;

    l *= 2;
    s *= l <= 1 ? l : 2 - l;
    _v = (l + s) / 2;
    _s = 2 * s / (l + s);

    return {
      h: _h,
      s: _s,
      v: _v
    };
  }

  function HSVtoRGB(h, s, v) {
    var r, g, b, i, f, p, q, t;
    if (arguments.length === 1) {
      s = h.s, v = h.v, h = h.h;
    }
    i = Math.floor(h * 6);
    f = h * 6 - i;
    p = v * (1 - s);
    q = v * (1 - f * s);
    t = v * (1 - (1 - f) * s);
    switch (i % 6) {
      case 0:
        r = v, g = t, b = p;
        break;
      case 1:
        r = q, g = v, b = p;
        break;
      case 2:
        r = p, g = v, b = t;
        break;
      case 3:
        r = p, g = q, b = v;
        break;
      case 4:
        r = t, g = p, b = v;
        break;
      case 5:
        r = v, g = p, b = q;
        break;
    }
    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
  }

  function kelvinToRGB(kelvin) {
    var temperature = kelvin / 100;
    var red;
    if (temperature <= 66) {
      red = 255;
    } else {
      red = temperature - 60;
      red = 329.698727446 * Math.pow(red, -0.1332047592);
      if (red < 0) red = 0;
      if (red > 255) red = 255;
    }

    var green;
    if (temperature <= 66) {
      green = temperature;
      green = 99.4708025861 * Math.log(green) - 161.1195681661;
      if (green < 0) green = 0;
      if (green > 255) green = 255;
    } else {
      green = temperature - 60;
      green = 288.1221695283 * Math.pow(green, -0.0755148492);
      if (green < 0) green = 0;
      if (green > 255) green = 255;
    }

    var blue;
    if (temperature >= 66) {
      blue = 255;
    } else {
      if (temperature <= 19) {
        blue = 0;
      } else {
        blue = temperature - 10;
        blue = 138.5177312231 * Math.log(blue) - 305.0447927307;
        if (blue < 0) blue = 0;
        if (blue > 255) blue = 255;
      }
    }

    return [red, green, blue];
  }

  if (saturation > 0.0) {
    return "hsl(" + hue + ", " + saturation * 100 + "%, 50%)";
  } else {
    var color = kelvinToRGB(kelvin);
    return "rgb(" + Math.round(color[0]) + ", " + Math.round(color[1]) + ", " + Math.round(color[2]) + ")";
  }
};

/***/ }),

/***/ "./js/index.js":
/*!*********************!*\
  !*** ./js/index.js ***!
  \*********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


__webpack_require__(/*! babel-core/register */ "./node_modules/babel-core/register.js");

__webpack_require__(/*! babel-polyfill */ "./node_modules/babel-polyfill/lib/index.js");

var _router = __webpack_require__(/*! ./router.js */ "./js/router.js");

var _wsclient = __webpack_require__(/*! ./wsclient.js */ "./js/wsclient.js");

var _history = __webpack_require__(/*! ./history.js */ "./js/history.js");

var _store = __webpack_require__(/*! ./store.js */ "./js/store.js");

var _effects = __webpack_require__(/*! redux-saga/effects */ "./node_modules/redux-saga/es/effects.js");

var _reactRedux = __webpack_require__(/*! react-redux */ "./node_modules/react-redux/es/index.js");

var _reactDom = __webpack_require__(/*! react-dom */ "./node_modules/react-dom/index.js");

var _reactDom2 = _interopRequireDefault(_reactDom);

var _react = __webpack_require__(/*! react */ "./node_modules/react/index.js");

var _react2 = _interopRequireDefault(_react);

__webpack_require__(/*! typeface-roboto */ "./node_modules/typeface-roboto/index.css");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var _marked = /*#__PURE__*/regeneratorRuntime.mark(mainSaga); // Do polyfills, must happen first


var reducer = (0, _store.makeReducer)();
var sagaMiddleware = (0, _store.makeSagaMiddleware)();
var store = (0, _store.makeStore)(reducer, sagaMiddleware);
(0, _store.runSagaMiddleware)(sagaMiddleware);

window.ReactDOM = _reactDom2.default;
window.Page = _react2.default.createElement(
  _reactRedux.Provider,
  { store: store },
  _react2.default.createElement(_router.Routes, { history: _history.history })
);

var scheme = "ws";
if (window.location.protocol.startsWith("https")) {
  scheme = "wss";
}
var url = scheme + "://" + window.location.hostname + ":" + String(window.location.port) + "/v1/ws";

function mainSaga() {
  return regeneratorRuntime.wrap(function mainSaga$(_context) {
    while (1) {
      switch (_context.prev = _context.next) {
        case 0:
          _context.next = 2;
          return (0, _effects.fork)(_wsclient.listen, url);

        case 2:
          _context.next = 4;
          return (0, _router.routerFork)(_history.history);

        case 4:
        case "end":
          return _context.stop();
      }
    }
  }, _marked, this);
}

sagaMiddleware.run(mainSaga);

/***/ }),

/***/ "./js/page.js":
/*!********************!*\
  !*** ./js/page.js ***!
  \********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _component = __webpack_require__(/*! ./control/component.js */ "./js/control/component.js");

var _propTypes = __webpack_require__(/*! prop-types */ "./node_modules/prop-types/index.js");

var _propTypes2 = _interopRequireDefault(_propTypes);

var _react = __webpack_require__(/*! react */ "./node_modules/react/index.js");

var _react2 = _interopRequireDefault(_react);

var _styles = __webpack_require__(/*! @material-ui/core/styles */ "./node_modules/@material-ui/core/styles/index.js");

var _Typography = __webpack_require__(/*! @material-ui/core/Typography */ "./node_modules/@material-ui/core/Typography/index.js");

var _Typography2 = _interopRequireDefault(_Typography);

var _IconButton = __webpack_require__(/*! @material-ui/core/IconButton */ "./node_modules/@material-ui/core/IconButton/index.js");

var _IconButton2 = _interopRequireDefault(_IconButton);

var _withWidth = __webpack_require__(/*! @material-ui/core/withWidth */ "./node_modules/@material-ui/core/withWidth/index.js");

var _withWidth2 = _interopRequireDefault(_withWidth);

var _Toolbar = __webpack_require__(/*! @material-ui/core/Toolbar */ "./node_modules/@material-ui/core/Toolbar/index.js");

var _Toolbar2 = _interopRequireDefault(_Toolbar);

var _Menu = __webpack_require__(/*! @material-ui/icons/Menu */ "./node_modules/@material-ui/icons/Menu.js");

var _Menu2 = _interopRequireDefault(_Menu);

var _AppBar = __webpack_require__(/*! @material-ui/core/AppBar */ "./node_modules/@material-ui/core/AppBar/index.js");

var _AppBar2 = _interopRequireDefault(_AppBar);

var _Grid = __webpack_require__(/*! @material-ui/core/Grid */ "./node_modules/@material-ui/core/Grid/index.js");

var _Grid2 = _interopRequireDefault(_Grid);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

var styles = function styles(theme) {
  return {
    root: _defineProperty({
      flexGrow: 1,
      height: 430,
      zIndex: 1,
      overflow: "hidden",
      position: "relative",
      display: "flex"
    }, "height", "100vh"),
    content: {
      flexGrow: 1,
      height: "100vh",
      backgroundColor: theme.palette.background.default,
      padding: theme.spacing.unit * 3,
      minWidth: 0 // So the Typography noWrap works
    },
    menuButton: {
      marginLeft: -12,
      marginRight: 20
    },
    toolbar: theme.mixins.toolbar,
    appBar: {
      zIndex: theme.zIndex.drawer + 1
    }
  };
};

var Page = function Page(_ref) {
  var width = _ref.width,
      children = _ref.children,
      classes = _ref.classes;

  return _react2.default.createElement(
    "div",
    null,
    _react2.default.createElement(
      "div",
      { className: classes.root },
      _react2.default.createElement(
        _AppBar2.default,
        { position: "absolute", className: classes.appBar },
        _react2.default.createElement(
          _Toolbar2.default,
          null,
          _react2.default.createElement(
            _IconButton2.default,
            {
              className: classes.menuButton,
              color: "inherit",
              "aria-label": "Menu"
            },
            _react2.default.createElement(_Menu2.default, null)
          ),
          _react2.default.createElement(
            _Typography2.default,
            { variant: "title", color: "inherit", noWrap: true },
            "Interactor"
          )
        )
      ),
      _react2.default.createElement(
        "main",
        { className: classes.content },
        _react2.default.createElement("div", { className: classes.toolbar }),
        children
      ),
      _react2.default.createElement(_component.ControlPane, null)
    )
  );
};

Page.propTypes = {
  classes: _propTypes2.default.object.isRequired
};

exports.default = (0, _withWidth2.default)()((0, _styles.withStyles)(styles)(Page));

/***/ }),

/***/ "./js/router.js":
/*!**********************!*\
  !*** ./js/router.js ***!
  \**********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function(React) {

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.Routes = exports.routerFork = exports.routes = undefined;

var _state = __webpack_require__(/*! ./device/state.js */ "./js/device/state.js");

var _dashboard = __webpack_require__(/*! ./dashboard.js */ "./js/dashboard.js");

var _dashboard2 = _interopRequireDefault(_dashboard);

var _page = __webpack_require__(/*! ./page.js */ "./js/page.js");

var _page2 = _interopRequireDefault(_page);

var _reactRouter = __webpack_require__(/*! react-router */ "./node_modules/react-router/es/index.js");

var _effects = __webpack_require__(/*! redux-saga/effects */ "./node_modules/redux-saga/es/effects.js");

var _reduxSagaRouter = __webpack_require__(/*! redux-saga-router */ "./node_modules/redux-saga-router/lib/index.js");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var routes = exports.routes = {
  "/": /*#__PURE__*/regeneratorRuntime.mark(function indexSaga() {
    return regeneratorRuntime.wrap(function indexSaga$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            _context.next = 2;
            return (0, _effects.put)(_state.DevicesState.GetSerials());

          case 2:
            _context.next = 4;
            return (0, _effects.put)(_state.DevicesState.GetDetails());

          case 4:
          case "end":
            return _context.stop();
        }
      }
    }, indexSaga, this);
  })
};

var routerFork = exports.routerFork = function routerFork(history) {
  return (0, _effects.fork)(_reduxSagaRouter.router, history, routes);
};

var Routes = exports.Routes = function Routes(_ref) {
  var history = _ref.history;
  return React.createElement(
    _reactRouter.Router,
    { history: history },
    React.createElement(
      _page2.default,
      null,
      React.createElement(
        _reactRouter.Switch,
        null,
        React.createElement(_reactRouter.Route, { exact: true, path: "/", component: _dashboard2.default })
      )
    )
  );
};
/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! react */ "./node_modules/react/index.js")))

/***/ }),

/***/ "./js/selection/state.js":
/*!*******************************!*\
  !*** ./js/selection/state.js ***!
  \*******************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.SelectionState = undefined;

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

exports.selectionSaga = selectionSaga;

var _wsclient = __webpack_require__(/*! ../wsclient.js */ "./js/wsclient.js");

var _effects = __webpack_require__(/*! redux-saga/effects */ "./node_modules/redux-saga/es/effects.js");

var _reduxAct = __webpack_require__(/*! redux-act */ "./node_modules/redux-act/lib/index.js");

var _reduxSaga = __webpack_require__(/*! redux-saga */ "./node_modules/redux-saga/es/index.js");

var _marked = /*#__PURE__*/regeneratorRuntime.mark(setTransformSaga),
    _marked2 = /*#__PURE__*/regeneratorRuntime.mark(askForDetailsSaga),
    _marked3 = /*#__PURE__*/regeneratorRuntime.mark(selectionSaga);

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var SelectionStateKls = function () {
  function SelectionStateKls() {
    _classCallCheck(this, SelectionStateKls);

    this.SetPower = (0, _reduxAct.createAction)("Set power", function (power) {
      return {
        transform: { power: power ? "on" : "off" }
      };
    });
    this.ChangeState = (0, _reduxAct.createAction)("Change state", function (transform, components) {
      return {
        transform: transform,
        components: components
      };
    });
    this.GotState = (0, _reduxAct.createAction)("Got state from a light");
    this.StartWaiting = (0, _reduxAct.createAction)("Start waiting");
    this.StopWaiting = (0, _reduxAct.createAction)("Stop waiting");
    this.ToggleWheel = (0, _reduxAct.createAction)("Toggle the wheel", function (white) {
      return { white: white };
    });
    this.ToggleSelection = (0, _reduxAct.createAction)("Toggle a selection");
    this.StateChangeError = (0, _reduxAct.createAction)("Error changing state");
    this.ClearError = (0, _reduxAct.createAction)("Clear error");
  }

  _createClass(SelectionStateKls, [{
    key: "reducer",
    value: function reducer() {
      var _createReducer;

      return (0, _reduxAct.createReducer)((_createReducer = {}, _defineProperty(_createReducer, this.ToggleSelection, function (state, _ref) {
        var serial = _ref.serial;

        var selection = _extends({}, state.selection);
        if (selection[serial]) {
          delete selection[serial];
        } else {
          selection[serial] = true;
        }
        return _extends({}, state, {
          selection: selection,
          state_number: state.state_number + 1,
          waiting: Object.keys(selection) === 0,
          light_state: _extends({}, state.light_state, state.light_state_buf)
        });
      }), _defineProperty(_createReducer, this.StartWaiting, function (state, payload) {
        return _extends({}, state, { waiting: true });
      }), _defineProperty(_createReducer, this.StopWaiting, function (state, _ref2) {
        var state_number = _ref2.state_number;

        var waiting = state.waiting;
        if (state_number === state.state_number) {
          waiting = false;
        }
        return _extends({}, state, {
          waiting: waiting,
          state_number: state.state_number + 1
        });
      }), _defineProperty(_createReducer, this.ToggleWheel, function (state, _ref3) {
        var white = _ref3.white;

        return _extends({}, state, {
          white: white,
          light_state: _extends({}, state.light_state, state.light_state_buf)
        });
      }), _defineProperty(_createReducer, this.GotState, function (state, _ref4) {
        var state_number = _ref4.state_number,
            serial = _ref4.serial,
            data = _ref4.data;

        if (state.state_number !== state_number) {
          return state;
        }

        var serials = Object.keys(state.selection);
        if (serials.length !== 1 || serials[0] !== serial) {
          return state;
        }

        return _extends({}, state, {
          light_state: data,
          light_state_buf: data,
          waiting: false
        });
      }), _defineProperty(_createReducer, this.StateChangeError, function (state, _ref5) {
        var error = _ref5.error,
            error_code = _ref5.error_code;

        var errormsg = error_code + ": " + JSON.stringify(error);
        return _extends({}, state, { error: errormsg });
      }), _defineProperty(_createReducer, this.ClearError, function (state, payload) {
        return _extends({}, state, { error: undefined });
      }), _defineProperty(_createReducer, this.ChangeState, function (state, _ref6) {
        var components = _ref6.components;

        return _extends({}, state, {
          state_number: state.state_number + 1,
          light_state_buf: _extends({}, state.light_state_buf, components)
        });
      }), _createReducer), {
        selection: {},
        error: undefined,
        light_state_buf: {},
        state_number: 0,
        white: false,
        waiting: false,
        light_state: {
          on: true,
          hue: 0,
          saturation: 1,
          brightness: 0.5,
          kelvin: 3500
        }
      });
    }
  }]);

  return SelectionStateKls;
}();

var SelectionState = exports.SelectionState = new SelectionStateKls();

function setTransformSaga(original) {
  var payload, onerror, state, selection, matcher;
  return regeneratorRuntime.wrap(function setTransformSaga$(_context) {
    while (1) {
      switch (_context.prev = _context.next) {
        case 0:
          payload = original.payload;
          onerror = SelectionState.StateChangeError;
          _context.next = 4;
          return (0, _effects.select)();

        case 4:
          state = _context.sent;
          selection = state.selection.selection;
          matcher = { serial: Object.keys(selection) };
          _context.next = 9;
          return (0, _effects.put)((0, _wsclient.WSCommand)("/v1/lifx/command", {
            command: "transform",
            args: { matcher: matcher, transform: payload.transform }
          }, { onerror: onerror, original: original }));

        case 9:
        case "end":
          return _context.stop();
      }
    }
  }, _marked, this);
}

function askForDetailsSaga(original) {
  var state, selection, serial, state_number, onsuccess, onerror;
  return regeneratorRuntime.wrap(function askForDetailsSaga$(_context2) {
    while (1) {
      switch (_context2.prev = _context2.next) {
        case 0:
          _context2.next = 2;
          return (0, _effects.select)();

        case 2:
          state = _context2.sent;
          selection = Object.keys(state.selection.selection);

          if (!(selection.length !== 1)) {
            _context2.next = 6;
            break;
          }

          return _context2.abrupt("return");

        case 6:
          serial = selection[0];
          _context2.next = 9;
          return (0, _effects.put)(SelectionState.StartWaiting());

        case 9:
          _context2.next = 11;
          return (0, _effects.select)();

        case 11:
          state = _context2.sent;
          state_number = state.selection.state_number;

          onsuccess = function onsuccess(_ref7) {
            var data = _ref7.data;

            var results = data.results[serial];
            if (results) {
              var payload = results.payload;
              var hue = payload.hue,
                  saturation = payload.saturation,
                  brightness = payload.brightness,
                  kelvin = payload.kelvin;

              var data = {
                on: payload.power !== 0,
                hue: hue,
                saturation: saturation,
                brightness: brightness,
                kelvin: kelvin
              };
              return SelectionState.GotState({ data: data, serial: serial, state_number: state_number });
            }
          };

          onerror = function onerror(_ref8) {
            var error = _ref8.error;
            return console.error(error);
          };

          _context2.next = 17;
          return (0, _effects.put)((0, _wsclient.WSCommand)("/v1/lifx/command", {
            command: "query",
            args: { matcher: { serial: serial }, pkt_type: "GetColor" }
          }, { onerror: onerror, onsuccess: onsuccess, original: original }));

        case 17:
          _context2.next = 19;
          return (0, _effects.call)(_reduxSaga.delay, 1000);

        case 19:
          _context2.next = 21;
          return (0, _effects.put)(SelectionState.StopWaiting({ state_number: state_number }));

        case 21:
        case "end":
          return _context2.stop();
      }
    }
  }, _marked2, this);
}

function selectionSaga() {
  return regeneratorRuntime.wrap(function selectionSaga$(_context3) {
    while (1) {
      switch (_context3.prev = _context3.next) {
        case 0:
          _context3.next = 2;
          return (0, _effects.takeLatest)([SelectionState.SetPower, SelectionState.ChangeState], setTransformSaga);

        case 2:
          _context3.next = 4;
          return (0, _effects.takeLatest)(SelectionState.ToggleSelection, askForDetailsSaga);

        case 4:
        case "end":
          return _context3.stop();
      }
    }
  }, _marked3, this);
}

/***/ }),

/***/ "./js/store.js":
/*!*********************!*\
  !*** ./js/store.js ***!
  \*********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.runSagaMiddleware = exports.makeStore = exports.makeSagaMiddleware = exports.makeReducer = undefined;

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _state = __webpack_require__(/*! ./device/state.js */ "./js/device/state.js");

var _state2 = __webpack_require__(/*! ./selection/state.js */ "./js/selection/state.js");

var _reduxDevtoolsExtension = __webpack_require__(/*! redux-devtools-extension */ "./node_modules/redux-devtools-extension/index.js");

var _redux = __webpack_require__(/*! redux */ "./node_modules/redux/es/redux.js");

var _reduxSaga = __webpack_require__(/*! redux-saga */ "./node_modules/redux-saga/es/index.js");

var _reduxSaga2 = _interopRequireDefault(_reduxSaga);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var makeReducer = exports.makeReducer = function makeReducer(extra) {
  return (0, _redux.combineReducers)(_extends({}, extra, {
    devices: _state.DevicesState.reducer(),
    selection: _state2.SelectionState.reducer()
  }));
};

var makeSagaMiddleware = exports.makeSagaMiddleware = function makeSagaMiddleware() {
  return (0, _reduxSaga2.default)();
};

var makeStore = exports.makeStore = function makeStore(reducer, sagaMiddleware) {
  var creator = (0, _redux.applyMiddleware)(sagaMiddleware)(_redux.createStore);
  return creator(reducer, (0, _reduxDevtoolsExtension.devToolsEnhancer)());
};

var runSagaMiddleware = exports.runSagaMiddleware = function runSagaMiddleware(sagaMiddleware) {
  sagaMiddleware.run(_state.deviceSaga);
  sagaMiddleware.run(_state2.selectionSaga);
};

/***/ }),

/***/ "./js/wheel/tween.js":
/*!***************************!*\
  !*** ./js/wheel/tween.js ***!
  \***************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = undefined;

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }(); //
//
//  Copied from https://github.com/chenglou/react-tween-state
//
//

var _tweenFunctions = __webpack_require__(/*! tween-functions */ "./node_modules/tween-functions/index.js");

var _raf = __webpack_require__(/*! raf */ "./node_modules/raf/index.js");

var _raf2 = _interopRequireDefault(_raf);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

// additive is the new iOS 8 default. In most cases it simulates a physics-
// looking overshoot behavior (especially with easeInOut. You can test that in
// the example
var DEFAULT_STACK_BEHAVIOR = "ADDITIVE";
var DEFAULT_EASING = _tweenFunctions.easeInOutQuad;
var DEFAULT_DURATION = 300;
var DEFAULT_DELAY = 0;

var stackBehavior = {
  ADDITIVE: "ADDITIVE",
  DESTRUCTIVE: "DESTRUCTIVE"
};

var Tweener = function () {
  function Tweener(wheel) {
    _classCallCheck(this, Tweener);

    this.wheel = wheel;
    this._rafID = null;
  }

  _createClass(Tweener, [{
    key: "getInitialState",
    value: function getInitialState() {
      return {
        tweenQueue: []
      };
    }
  }, {
    key: "componentWillUnmount",
    value: function componentWillUnmount() {
      _raf2.default.cancel(this._rafID);
      this._rafID = -1;
    }
  }, {
    key: "tweenState",
    value: function tweenState(path, _ref) {
      var _this = this;

      var easing = _ref.easing,
          duration = _ref.duration,
          delay = _ref.delay,
          beginValue = _ref.beginValue,
          endValue = _ref.endValue,
          onEnd = _ref.onEnd,
          configSB = _ref.stackBehavior;

      this.wheel.setState(function (state) {
        var cursor = state;
        var stateName = void 0;
        // see comment below on pash hash
        var pathHash = void 0;
        if (typeof path === "string") {
          stateName = path;
          pathHash = path;
        } else {
          for (var i = 0; i < path.length - 1; i++) {
            cursor = cursor[path[i]];
          }
          stateName = path[path.length - 1];
          pathHash = path.join("|");
        }
        // see the reasoning for these defaults at the top of file
        var newConfig = {
          easing: easing || DEFAULT_EASING,
          duration: duration == null ? DEFAULT_DURATION : duration,
          delay: delay == null ? DEFAULT_DELAY : delay,
          beginValue: beginValue == null ? cursor[stateName] : beginValue,
          endValue: endValue,
          onEnd: onEnd,
          stackBehavior: configSB || DEFAULT_STACK_BEHAVIOR
        };

        var newTweenQueue = state.tweenQueue;
        if (newConfig.stackBehavior === stackBehavior.DESTRUCTIVE) {
          newTweenQueue = state.tweenQueue.filter(function (item) {
            return item.pathHash !== pathHash;
          });
        }

        // we store path hash, so that during value retrieval we can use hash
        // comparison to find the path. See the kind of shitty thing you have to
        // do when you don't have value comparison for collections?
        newTweenQueue.push({
          pathHash: pathHash,
          config: newConfig,
          initTime: Date.now() + newConfig.delay
        });

        // sorry for mutating. For perf reasons we don't want to deep clone.
        // guys, can we please all start using persistent collections so that
        // we can stop worrying about nonesense like this
        cursor[stateName] = newConfig.endValue;
        if (newTweenQueue.length === 1) {
          _this._rafID = (0, _raf2.default)(_this._rafCb.bind(_this));
        }

        // this will also include the above mutated update
        return { tweenQueue: newTweenQueue };
      });
    }
  }, {
    key: "getTweeningValue",
    value: function getTweeningValue(path) {
      var state = this.wheel.state;

      var tweeningValue = void 0;
      var pathHash = void 0;
      if (typeof path === "string") {
        tweeningValue = state[path];
        pathHash = path;
      } else {
        tweeningValue = state;
        for (var i = 0; i < path.length; i++) {
          tweeningValue = tweeningValue[path[i]];
        }
        pathHash = path.join("|");
      }
      var now = Date.now();

      for (var _i = 0; _i < state.tweenQueue.length; _i++) {
        var _state$tweenQueue$_i = state.tweenQueue[_i],
            itemPathHash = _state$tweenQueue$_i.pathHash,
            initTime = _state$tweenQueue$_i.initTime,
            config = _state$tweenQueue$_i.config;

        if (itemPathHash !== pathHash) {
          continue;
        }

        var progressTime = now - initTime > config.duration ? config.duration : Math.max(0, now - initTime);
        // `now - initTime` can be negative if initTime is scheduled in the
        // future by a delay. In this case we take 0

        // if duration is 0, consider that as jumping to endValue directly. This
        // is needed because the easing functino might have undefined behavior for
        // duration = 0
        var easeValue = config.duration === 0 ? config.endValue : config.easing(progressTime, config.beginValue, config.endValue, config.duration
        // TODO: some funcs accept a 5th param
        );
        var contrib = easeValue - config.endValue;
        tweeningValue += contrib;
      }

      return tweeningValue;
    }
  }, {
    key: "_rafCb",
    value: function _rafCb() {
      var state = this.wheel.state;
      if (state.tweenQueue.length === 0) {
        return;
      }

      var now = Date.now();
      var newTweenQueue = [];

      for (var i = 0; i < state.tweenQueue.length; i++) {
        var item = state.tweenQueue[i];
        var initTime = item.initTime,
            config = item.config;

        if (now - initTime < config.duration) {
          newTweenQueue.push(item);
        } else {
          config.onEnd && config.onEnd();
        }
      }

      // onEnd might trigger a parent callback that removes this component
      // -1 means we've canceled it in componentWillUnmount
      if (this._rafID === -1) {
        return;
      }

      this.wheel.setState({
        tweenQueue: newTweenQueue
      });

      this._rafID = (0, _raf2.default)(this._rafCb.bind(this));
    }
  }]);

  return Tweener;
}();

exports.default = Tweener;

/***/ }),

/***/ "./js/wheel/wheel.js":
/*!***************************!*\
  !*** ./js/wheel/wheel.js ***!
  \***************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ColourPicker = undefined;

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _hskToColor = __webpack_require__(/*! ../hsk-to-color.js */ "./js/hsk-to-color.js");

var _hskToColor2 = _interopRequireDefault(_hskToColor);

var _tween = __webpack_require__(/*! ./tween.js */ "./js/wheel/tween.js");

var _tween2 = _interopRequireDefault(_tween);

var _tweenFunctions = __webpack_require__(/*! tween-functions */ "./node_modules/tween-functions/index.js");

var _tweenFunctions2 = _interopRequireDefault(_tweenFunctions);

var _react = __webpack_require__(/*! react */ "./node_modules/react/index.js");

var _react2 = _interopRequireDefault(_react);

var _reactKonva = __webpack_require__(/*! react-konva */ "./node_modules/react-konva/lib/index.js");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /*
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * This work is licensed under NonCommercial-ShareAlike 4.0 International
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * (CC BY-NC-SA 4.0). The 'LIFX Colour Wheel' patented design as intellectual
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * property is used in this repository.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                *
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * LIFX has granted permission to use the 'LIFX Colour Wheel' design conditional
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * on use of the (CC BY-NC-SA 4.0) license.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                *
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Commercial use the 'LIFX Colour Wheel' requires written consent from LIFX.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Submit enquiries to business@lifx.com
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */

var whites = [[1500, "Candlelight"], [2000, "Sunset"], [2500, "Ultra Warm"], [2750, "Incandescent"], [3000, "Warm"], [3200, "Neutral Warm"], [3500, "Neutral"], [4000, "Cool"], [4500, "Cool Daylight"], [5000, "Soft Daylight"], [5500, "Daylight"], [6000, "Noon Daylight"], [6500, "Bright Daylight"], [7000, "Cloudy Daylight"], [7500, "Blue Daylight"], [8000, "Blue Overcast"], [8500, "Blue Water"], [9000, "Blue Ice"]];

var normaldwhites = [whites[0]];
for (var i = 0; i < whites.length - 1; i++) {
  var diff = whites[i + 1][0] - whites[i][0];
  normaldwhites.push([Math.round(whites[i + 1][0] - diff / 2), whites[i + 1][1]]);
}

function angle_to_kelvin(angle) {
  return Math.round(1500 + (9000 - 1500) * (angle / 360));
}

function kelvin_to_angle(kelvin) {
  return (kelvin - 1500) * 360 / (9000 - 1500);
}

function normal_hue(hue) {
  while (hue < 0) {
    hue += 360;
  }
  return hue % 360;
}

function getPos(el) {
  for (var lx = 0, ly = 0; el != null; lx += el.offsetLeft, ly += el.offsetTop, el = el.offsetParent) {}
  return { x: lx, y: ly };
}

var Power = function (_React$Component) {
  _inherits(Power, _React$Component);

  function Power(props) {
    _classCallCheck(this, Power);

    var _this = _possibleConstructorReturn(this, (Power.__proto__ || Object.getPrototypeOf(Power)).call(this, props));

    _this.state = { on: props.on };
    props.events.onPowerChange = _this.clicked.bind(_this);
    return _this;
  }

  _createClass(Power, [{
    key: "clicked",
    value: function clicked(click) {
      var new_on = !this.state.on;
      if (click !== false) {
        this.props.onClick();
      }
      this.setState({ on: new_on });
    }
  }, {
    key: "render",
    value: function render() {
      var _props = this.props,
          center_x = _props.center_x,
          center_y = _props.center_y,
          inner_radius = _props.inner_radius,
          outer_radius = _props.outer_radius;

      var arc_top = this.props.height - (outer_radius - inner_radius) / 2 - 5;
      return _react2.default.createElement(
        _reactKonva.Group,
        null,
        _react2.default.createElement(_reactKonva.Arc, {
          onClick: this.clicked.bind(this),
          angle: 70,
          rotation: 90 - 35,
          x: center_x,
          y: center_y,
          fill: "#4d5866",
          innerRadius: inner_radius,
          outerRadius: outer_radius
        }),
        _react2.default.createElement(_reactKonva.Arc, {
          onClick: this.clicked.bind(this),
          x: this.props.width / 2,
          y: arc_top,
          angle: 280,
          rotation: -90 + 40,
          innerRadius: 12,
          outerRadius: 15,
          fill: this.state.on ? "#009EFD" : "white"
        }),
        _react2.default.createElement(_reactKonva.Line, {
          onClick: this.clicked.bind(this),
          points: [this.props.width / 2, arc_top - 10, this.props.width / 2, arc_top],
          stroke: this.state.on ? "#009EFD" : "white",
          strokeWidth: 3
        })
      );
    }
  }]);

  return Power;
}(_react2.default.Component);

var DraggableArc = function (_React$Component2) {
  _inherits(DraggableArc, _React$Component2);

  function DraggableArc() {
    _classCallCheck(this, DraggableArc);

    return _possibleConstructorReturn(this, (DraggableArc.__proto__ || Object.getPrototypeOf(DraggableArc)).apply(this, arguments));
  }

  _createClass(DraggableArc, [{
    key: "clickArcs",
    value: function clickArcs(e) {
      var offset = getPos(e.target.getStage().attrs.container);
      var s_x = e.evt.clientX - offset.x;
      var s_y = e.evt.clientY - offset.y;

      var nodes = e.target.getParent().getChildren();
      var point = { x: s_x, y: s_y };

      var hue = 0;
      for (var i = 0; i <= 360; i++) {
        if (nodes[i].intersects(point)) {
          hue = nodes[i].attrs.rotation;
          break;
        }
      }
      this.props.onClick(hue);
    }
  }, {
    key: "render",
    value: function render() {
      var _this3 = this;

      var _props2 = this.props,
          hue = _props2.hue,
          on = _props2.on,
          center_x = _props2.center_x,
          center_y = _props2.center_y,
          inner_radius = _props2.inner_radius,
          outer_radius = _props2.outer_radius,
          white = _props2.white;


      var arcs = [];
      for (var angle = 0; angle <= 360; angle += 1) {
        var color = "hsl(" + angle + ", " + (on ? 100 : 30) + "%, 50%)";
        if (white) {
          color = (0, _hskToColor2.default)(angle, 0, angle_to_kelvin(angle));
        }
        arcs.push(_react2.default.createElement(_reactKonva.Arc, {
          key: angle,
          angle: 3,
          rotation: angle,
          x: center_x,
          y: center_y,
          innerRadius: inner_radius,
          outerRadius: outer_radius,
          fill: color
        }));
      }

      var cover_circle_gradient_stops = [0, on ? "white" : "rgba(255,255,255,0)", 1, "rgba(255,255,255,0)"];
      if (white) {
        var black_cover = on ? "rgba(255,255,255,0" : "rgba(0,0,0,0.3)";
        cover_circle_gradient_stops = [0, black_cover, 1, black_cover];
      }

      return _react2.default.createElement(
        _reactKonva.Group,
        {
          ref: function ref(o) {
            _this3.props.refs.draggable_arcs = o;
          },
          draggable: true,
          dragBoundFunc: function dragBoundFunc(pos) {
            return { x: center_x, y: center_y };
          },
          onDragStart: this.props.onDragStart,
          onDragMove: this.props.onDragMove,
          onDragEnd: this.props.onDragEnd,
          offset: { x: center_x, y: center_y },
          rotation: -((hue + 90) % 360),
          x: center_x,
          y: center_y
        },
        arcs,
        _react2.default.createElement(_reactKonva.Arc, {
          angle: 360,
          x: center_x,
          y: center_y,
          onClick: this.clickArcs.bind(this),
          innerRadius: inner_radius,
          outerRadius: outer_radius,
          fillRadialGradientStartRadius: inner_radius,
          fillRadialGradientEndRadius: outer_radius,
          fillRadialGradientColorStops: cover_circle_gradient_stops
        })
      );
    }
  }]);

  return DraggableArc;
}(_react2.default.Component);

var Brightness = function (_React$Component3) {
  _inherits(Brightness, _React$Component3);

  function Brightness() {
    _classCallCheck(this, Brightness);

    return _possibleConstructorReturn(this, (Brightness.__proto__ || Object.getPrototypeOf(Brightness)).apply(this, arguments));
  }

  _createClass(Brightness, [{
    key: "componentDidMount",
    value: function componentDidMount() {
      this.props.refs.brightness_lines.move({
        x: 0,
        y: -(this.props.height * this.props.brightness)
      });
    }
  }, {
    key: "render",
    value: function render() {
      var _this5 = this;

      var _props3 = this.props,
          refs = _props3.refs,
          brightness = _props3.brightness,
          height = _props3.height,
          center_x = _props3.center_x,
          center_y = _props3.center_y,
          inner_radius = _props3.inner_radius,
          outer_radius = _props3.outer_radius;


      var pos_y = center_y - height * brightness;

      var lines = [];
      for (var _i = 0; _i < 16; _i++) {
        var y = _i * (this.props.height / 15) + pos_y;
        var l = 100 - Math.round(100 * Math.abs(y - center_y) / center_y);
        var stroke = "hsl(0,0%," + l + "%)";
        lines.push({ i: _i, y: y, stroke: stroke });
      }

      return _react2.default.createElement(
        _reactKonva.Group,
        null,
        _react2.default.createElement(
          _reactKonva.Group,
          {
            clipFunc: function clipFunc(ctx) {
              ctx.arc(center_x, center_y, inner_radius, 0, Math.PI * 2, false);
            }
          },
          _react2.default.createElement(_reactKonva.Circle, {
            x: center_x,
            y: center_y,
            radius: inner_radius,
            fillRadialGradientStartRadius: inner_radius,
            fillRadialGradientEndRadius: outer_radius,
            fillRadialGradientColorStops: [0, "#6e7d91", 1, "#4d5866"],
            fillRadialGradientStartPoint: {
              x: 0,
              y: 0
            },
            fillRadialGradientEndPoint: {
              x: 90,
              y: 90
            }
          }),
          _react2.default.createElement(
            _reactKonva.Group,
            {
              ref: function ref(o) {
                refs.brightness_lines = o;
              },
              draggable: true,
              dragBoundFunc: function dragBoundFunc(pos) {
                var y = pos.y;
                if (y > -(_this5.props.height * 0.01)) {
                  y = -(_this5.props.height * 0.01);
                }

                if (y < -_this5.props.height) {
                  y = -_this5.props.height;
                }

                return { x: 0, y: y };
              },
              onDragMove: this.props.onDragMove
            },
            _react2.default.createElement(_reactKonva.Rect, {
              x: 0,
              y: 0,
              width: this.props.width,
              height: this.props.height * 3
            })
          ),
          _react2.default.createElement(
            _reactKonva.Group,
            null,
            lines.map(function (l) {
              return _react2.default.createElement(_reactKonva.Line, {
                key: l.i,
                points: [center_x - 10, l.y, center_x + 10, l.y],
                stroke: l.stroke,
                strokeWidth: 1
              });
            })
          )
        )
      );
    }
  }]);

  return Brightness;
}(_react2.default.Component);

var SaturationControl = function (_React$Component4) {
  _inherits(SaturationControl, _React$Component4);

  function SaturationControl() {
    _classCallCheck(this, SaturationControl);

    return _possibleConstructorReturn(this, (SaturationControl.__proto__ || Object.getPrototypeOf(SaturationControl)).apply(this, arguments));
  }

  _createClass(SaturationControl, [{
    key: "render",
    value: function render() {
      var _this7 = this;

      var _props4 = this.props,
          center_x = _props4.center_x,
          center_y = _props4.center_y,
          inner_radius = _props4.inner_radius,
          outer_radius = _props4.outer_radius,
          on = _props4.on,
          hue = _props4.hue,
          saturation = _props4.saturation;


      var l = 1 - saturation;
      if (l > 0.8) {
        l = 0.8;
      }
      var white_color = "rgba(255,255,255," + l + ")";

      var color = "hsl(" + hue + ",100%,50%)";
      var min_y = 15;
      var max_y = center_y - inner_radius - 15;
      var y_pos = max_y - (max_y - min_y) * saturation;

      return _react2.default.createElement(
        _reactKonva.Layer,
        null,
        _react2.default.createElement(_reactKonva.Line, {
          points: [center_x, center_y - outer_radius, center_x, center_y - inner_radius],
          stroke: "black",
          strokeWidth: 3
        }),
        _react2.default.createElement(_reactKonva.Circle, {
          x: center_x,
          y: y_pos,
          radius: 15,
          fill: color,
          stroke: on ? "white" : "black",
          strokeWidth: 2
        }),
        _react2.default.createElement(_reactKonva.Circle, {
          ref: function ref(o) {
            _this7.props.refs.saturation_circle = o;
          },
          draggable: true,
          dragBoundFunc: function dragBoundFunc(pos) {
            var y = pos.y;

            var min_y = 15;
            if (y < min_y) {
              y = min_y;
            }

            var max_y = center_y - inner_radius - 15;
            if (y > max_y) {
              y = max_y;
            }

            return { x: center_x, y: y };
          },
          onDragMove: this.props.onDragMove,
          x: center_x,
          y: y_pos,
          radius: 15,
          fill: white_color,
          stroke: on ? "white" : "black",
          strokeWidth: 2
        })
      );
    }
  }]);

  return SaturationControl;
}(_react2.default.Component);

var ColourPicker = exports.ColourPicker = function (_React$Component5) {
  _inherits(ColourPicker, _React$Component5);

  function ColourPicker(props) {
    _classCallCheck(this, ColourPicker);

    var _this8 = _possibleConstructorReturn(this, (ColourPicker.__proto__ || Object.getPrototypeOf(ColourPicker)).call(this, props));

    _this8.tweener = new _tween2.default(_this8);

    var hue = props.hue;
    if (props.white) {
      hue = kelvin_to_angle(props.kelvin);
    }

    _this8.state = Object.assign({}, {
      hue: hue,
      on: props.on,
      saturation: props.saturation,
      brightness: props.brightness
    }, _this8.tweener.getInitialState());
    _this8.events = {};

    _this8.last_angle = -hue * (Math.PI / 180);

    _this8.extra_refs = {};

    _this8.inner_radius = Math.round(_this8.props.height / 3.5);
    _this8.outer_radius = Math.round(_this8.props.height / 2);
    _this8.center_x = _this8.props.width / 2;
    _this8.center_y = _this8.props.height / 2;
    return _this8;
  }

  _createClass(ColourPicker, [{
    key: "componentDidUpdate",
    value: function componentDidUpdate() {
      if (this.state.isnewprops) {
        this.last_angle = -this.state.hue * (Math.PI / 180);
      }
    }
  }, {
    key: "componentWillUnmount",
    value: function componentWillUnmount() {
      this.tweener.componentWillUnmount();
    }
  }, {
    key: "submit",
    value: function submit(payload) {
      var args = { duration: 0.3 };
      var components = {};

      if (payload.hue !== undefined || payload.saturation != undefined || payload.brightness != undefined) {
        var hueval = payload.hue || this.state.hue;
        components.saturation = payload.saturation || this.state.saturation;
        components.brightness = payload.brightness || this.state.brightness;

        var sat = components.saturation.toFixed(2);
        var bright = components.brightness.toFixed(2);

        if (this.props.white) {
          components.kelvin = angle_to_kelvin(hueval);
          args.color = "saturation:0 kelvin:" + components.kelvin + " brightness:" + bright;
        } else {
          components.hue = normal_hue(hueval);
          args.color = "hue:" + components.hue.toFixed(2) + " saturation:" + sat + " brightness:" + bright;
        }
      }

      if (payload.power !== undefined) {
        args.power = payload.power ? "on" : "off";
      } else if (!this.state.on) {
        args.power = "on";
        this.setState({ on: true });
        this.events.onPowerChange(false);
      }

      if (args.power !== undefined) {
        components.on = args.power === "on";
      }

      this.props.submit(args, components);
    }
  }, {
    key: "power_clicked",
    value: function power_clicked() {
      var new_on = !this.state.on;
      this.setState({ on: new_on });
      this.submit({ power: new_on });
    }
  }, {
    key: "dragstart",
    value: function dragstart(e) {
      var offset = getPos(e.target.getStage().attrs.container);
      this.h_x = e.evt.clientX - offset.x;
      this.h_y = e.evt.clientY - offset.y;
    }
  }, {
    key: "dragmove",
    value: function dragmove(e) {
      var offset = getPos(e.target.getStage().attrs.container);
      var s_x = e.evt.clientX - offset.x;
      var s_y = e.evt.clientY - offset.y;
      var s_rad = Math.atan2(s_y - this.center_y, s_x - this.center_x);
      s_rad -= Math.atan2(this.h_y - this.center_y, this.h_x - this.center_x);
      s_rad += this.last_angle;
      var hue = normal_hue(-(s_rad * (180 / Math.PI)));
      this.setState({ hue: hue });
      this.submit({ hue: hue });
    }
  }, {
    key: "dragend",
    value: function dragend(e) {
      var offset = getPos(e.target.getStage().attrs.container);
      var s_x = e.evt.clientX - offset.x;
      var s_y = e.evt.clientY - offset.y;

      var s_rad = Math.atan2(s_y - this.center_y, s_x - this.center_x);
      s_rad -= Math.atan2(this.h_y - this.center_y, this.h_x - this.center_x);
      s_rad += this.last_angle;
      this.last_angle = s_rad;
    }
  }, {
    key: "drag_brightness",
    value: function drag_brightness(e) {
      var brightness = -(this.extra_refs.brightness_lines.attrs.y / this.props.height);
      this.setState({ brightness: brightness });
      this.submit({ brightness: brightness });
    }
  }, {
    key: "drag_saturation",
    value: function drag_saturation(e) {
      var min_y = 15;
      var max_y = this.center_y - this.inner_radius - 15;

      var saturation = (max_y - this.extra_refs.saturation_circle.attrs.y) / (max_y - min_y);

      this.setState({ saturation: saturation });
      this.submit({ saturation: saturation });
    }
  }, {
    key: "clickColours",
    value: function clickColours(hue) {
      var _this9 = this;

      var to_hue = hue;
      if (this.state.hue < hue && hue - this.state.hue > 180) {
        to_hue = hue - 360;
      } else if (this.state.hue > hue && this.state.hue - hue > 180) {
        to_hue = hue + 360;
      }

      this.tweener.tweenState("hue", {
        easing: _tweenFunctions2.default.easeInOutQuad,
        duration: 500,
        endValue: to_hue,
        onEnd: function onEnd() {
          return _this9.setState({ hue: hue });
        }
      });
      this.submit({ hue: hue });

      // And make sure when we start dragging again
      // It continues from the same place
      this.last_angle = -hue * (Math.PI / 180);
    }
  }, {
    key: "render",
    value: function render() {
      var hue = this.tweener.getTweeningValue("hue");
      var brightness = Math.round(this.state.brightness * 100);
      var kelvin = angle_to_kelvin(hue);

      var text = "Color " + Math.round(normal_hue(hue)) + "° - " + brightness + "%";
      if (this.props.white) {
        text = "Kelvin " + kelvin + " - " + brightness + "%";
      }

      var kelvinText = "";
      if (this.props.white) {
        for (var i = 0; i < normaldwhites.length; i++) {
          if (kelvin >= normaldwhites[i][0]) {
            kelvinText = normaldwhites[i][1];
          }
        }
      }

      var style = this.props.style || {};
      return _react2.default.createElement(
        "div",
        { style: style },
        _react2.default.createElement(
          _reactKonva.Stage,
          { width: this.props.width, height: this.props.white ? 60 : 30 },
          _react2.default.createElement(
            _reactKonva.Layer,
            null,
            _react2.default.createElement(_reactKonva.Text, {
              fontSize: 24,
              text: text,
              align: "center",
              width: this.props.width
            }),
            this.props.white ? _react2.default.createElement(_reactKonva.Text, {
              y: 30,
              fontSize: 24,
              text: kelvinText,
              align: "center",
              width: this.props.width
            }) : null
          )
        ),
        _react2.default.createElement(
          _reactKonva.Stage,
          { width: this.props.width, height: this.props.height },
          _react2.default.createElement(
            _reactKonva.Layer,
            null,
            _react2.default.createElement(Brightness, {
              refs: this.extra_refs,
              center_x: this.center_x,
              center_y: this.center_y,
              inner_radius: this.inner_radius,
              width: this.props.width,
              height: this.props.height,
              brightness: this.state.brightness,
              onDragMove: this.drag_brightness.bind(this)
            })
          ),
          _react2.default.createElement(
            _reactKonva.Layer,
            null,
            _react2.default.createElement(DraggableArc, {
              white: this.props.white,
              on: this.state.on,
              hue: this.tweener.getTweeningValue("hue"),
              inner_radius: this.inner_radius,
              outer_radius: this.outer_radius,
              refs: this.extra_refs,
              center_x: this.center_x,
              center_y: this.center_y,
              onClick: this.clickColours.bind(this),
              onDragStart: this.dragstart.bind(this),
              onDragMove: this.dragmove.bind(this),
              onDragEnd: this.dragend.bind(this)
            }),
            _react2.default.createElement(Power, {
              on: this.state.on,
              onClick: this.power_clicked.bind(this),
              events: this.events,
              width: this.props.width,
              height: this.props.height,
              center_x: this.center_x,
              center_y: this.center_y,
              inner_radius: this.inner_radius,
              outer_radius: this.outer_radius
            })
          ),
          this.props.white ? _react2.default.createElement(
            _reactKonva.Layer,
            null,
            _react2.default.createElement(_reactKonva.Line, {
              points: [this.center_x, this.center_y - this.outer_radius, this.center_x, this.center_y - this.inner_radius],
              stroke: "black",
              strokeWidth: 3
            })
          ) : _react2.default.createElement(SaturationControl, {
            center_x: this.center_x,
            center_y: this.center_y,
            inner_radius: this.inner_radius,
            outer_radius: this.outer_radius,
            onDragMove: this.drag_saturation.bind(this),
            refs: this.extra_refs,
            on: this.state.on,
            hue: this.tweener.getTweeningValue("hue"),
            saturation: this.state.saturation
          })
        )
      );
    }
  }], [{
    key: "getDerivedStateFromProps",
    value: function getDerivedStateFromProps(props, state) {
      var kelvin = props.kelvin,
          hue = props.hue,
          on = props.on,
          saturation = props.saturation,
          brightness = props.brightness,
          white = props.white;

      var isnewprops = state.oldprops === undefined || hue !== state.oldprops.hue || on !== state.oldprops.on || saturation !== state.oldprops.saturation || brightness !== state.oldprops.brightness || kelvin !== state.oldprops.kelvin || white !== state.oldprops.white;

      if (isnewprops) {
        var colorhue = state.colorhue;

        if (white) {
          colorhue = hue;
          hue = kelvin_to_angle(kelvin);
        } else {
          hue = state.colorhue || hue;
        }

        return {
          hue: hue,
          on: on,
          colorhue: colorhue,
          saturation: saturation,
          brightness: brightness,
          isnewprops: isnewprops,
          oldprops: props
        };
      }

      return { isnewprops: isnewprops };
    }
  }]);

  return ColourPicker;
}(_react2.default.Component);

/***/ }),

/***/ "./js/wsclient.js":
/*!************************!*\
  !*** ./js/wsclient.js ***!
  \************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.WSCommand = exports.WSState = undefined;

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

exports.getWSCommands = getWSCommands;
exports.listen = listen;

var _effects = __webpack_require__(/*! redux-saga/effects */ "./node_modules/redux-saga/es/effects.js");

var _reduxSaga = __webpack_require__(/*! redux-saga */ "./node_modules/redux-saga/es/index.js");

var _reduxAct = __webpack_require__(/*! redux-act */ "./node_modules/redux-act/lib/index.js");

var _v = __webpack_require__(/*! uuid/v4 */ "./node_modules/uuid/v4.js");

var _v2 = _interopRequireDefault(_v);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var _marked = /*#__PURE__*/regeneratorRuntime.mark(maybeTimeoutMessage),
    _marked2 = /*#__PURE__*/regeneratorRuntime.mark(sendToSocket),
    _marked3 = /*#__PURE__*/regeneratorRuntime.mark(tickMessages),
    _marked4 = /*#__PURE__*/regeneratorRuntime.mark(startWS),
    _marked5 = /*#__PURE__*/regeneratorRuntime.mark(processWsSend),
    _marked6 = /*#__PURE__*/regeneratorRuntime.mark(processWsReceive),
    _marked7 = /*#__PURE__*/regeneratorRuntime.mark(getWSCommands),
    _marked8 = /*#__PURE__*/regeneratorRuntime.mark(listen);

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var WSStateKls = function () {
  function WSStateKls() {
    _classCallCheck(this, WSStateKls);

    this.Loading = (0, _reduxAct.createAction)("Starting to open connection");
    this.Error = (0, _reduxAct.createAction)("Got an error connecting to the websocket");
    this.Connected = (0, _reduxAct.createAction)("Successfully connected to the websocket");
    this.ServerTime = (0, _reduxAct.createAction)("Got a new server time from the server", function (time) {
      return {
        time: time
      };
    });
  }

  _createClass(WSStateKls, [{
    key: "reducer",
    value: function reducer() {
      var _createReducer;

      return (0, _reduxAct.createReducer)((_createReducer = {}, _defineProperty(_createReducer, this.Loading, function (state, payload) {
        return _extends({}, state, { loading: true });
      }), _defineProperty(_createReducer, this.Error, function (state, _ref) {
        var error = _ref.error;

        return _extends({}, state, { error: error, loading: true });
      }), _defineProperty(_createReducer, this.Connected, function (state, payload) {
        return _extends({}, state, { error: undefined, loading: false });
      }), _createReducer), {
        error: undefined,
        devices: {},
        loading: true
      });
    }
  }]);

  return WSStateKls;
}();

var WSState = exports.WSState = new WSStateKls();

var WSCommand = exports.WSCommand = (0, _reduxAct.createAction)("Command to the websocket server", function (path, body, _ref2) {
  var onsuccess = _ref2.onsuccess,
      onerror = _ref2.onerror,
      onprogress = _ref2.onprogress,
      timeout = _ref2.timeout,
      original = _ref2.original;
  return {
    path: path,
    body: body,
    onsuccess: onsuccess,
    onerror: onerror,
    onprogress: onprogress,
    timeout: timeout,
    original: original
  };
});

function maybeTimeoutMessage(actions, messageId) {
  var action, response;
  return regeneratorRuntime.wrap(function maybeTimeoutMessage$(_context) {
    while (1) {
      switch (_context.prev = _context.next) {
        case 0:
          action = actions[messageId];
          _context.next = 3;
          return (0, _effects.call)(_reduxSaga.delay, action.timeout || 5000);

        case 3:
          _context.prev = 3;
          response = action.onerror({
            error: "Timedout waiting for a reply to the message",
            error_code: "Timedout"
          });

        case 5:
          _context.prev = 5;

          if (!response) {
            _context.next = 10;
            break;
          }

          _context.next = 9;
          return (0, _effects.put)(response);

        case 9:
          delete actions[messageId];

        case 10:
          return _context.finish(5);

        case 11:
        case "end":
          return _context.stop();
      }
    }
  }, _marked, this, [[3,, 5, 11]]);
}

function sendToSocket(socket, sendch, actions) {
  var action, response;
  return regeneratorRuntime.wrap(function sendToSocket$(_context2) {
    while (1) {
      switch (_context2.prev = _context2.next) {
        case 0:
          if (false) {}

          _context2.next = 3;
          return (0, _effects.take)(sendch);

        case 3:
          action = _context2.sent;

          if (!(socket.readyState === 1)) {
            _context2.next = 8;
            break;
          }

          socket.send(JSON.stringify(action.data));
          _context2.next = 16;
          break;

        case 8:
          _context2.prev = 8;
          response = action.onerror({
            error: "Connection to the server wasn't active",
            error_code: "InactiveConnection"
          });

        case 10:
          _context2.prev = 10;

          if (!response) {
            _context2.next = 15;
            break;
          }

          _context2.next = 14;
          return (0, _effects.put)(response);

        case 14:
          delete actions[action.messageId];

        case 15:
          return _context2.finish(10);

        case 16:
          _context2.next = 0;
          break;

        case 18:
        case "end":
          return _context2.stop();
      }
    }
  }, _marked2, this, [[8,, 10, 16]]);
}

function tickMessages(socket) {
  return regeneratorRuntime.wrap(function tickMessages$(_context3) {
    while (1) {
      switch (_context3.prev = _context3.next) {
        case 0:
          if (false) {}

          _context3.next = 3;
          return (0, _effects.call)(_reduxSaga.delay, 15000);

        case 3:
          if (socket.readyState === 1) {
            socket.send(JSON.stringify({ path: "__tick__" }));
          }
          _context3.next = 0;
          break;

        case 6:
        case "end":
          return _context3.stop();
      }
    }
  }, _marked3, this);
}

function startWS(url, count, sendch, receivech, actions) {
  var socket, onerrors, oncloses, ws, start, _ref3, timeout, w, diff, waiter, ticker, sender;

  return regeneratorRuntime.wrap(function startWS$(_context4) {
    while (1) {
      switch (_context4.prev = _context4.next) {
        case 0:
          socket = new WebSocket(url);
          onerrors = [];
          oncloses = [];
          ws = new Promise(function (resolve, reject) {
            socket.onopen = function () {
              resolve(socket);
            };

            socket.onmessage = function (event) {
              return receivech.put(event);
            };

            socket.onerror = function (evt) {
              console.error("Websocket got error", evt);
              reject(evt);
            };

            socket.onclose = function (evt) {
              console.error("Websocket closed", evt);
              reject(evt);
              oncloses.map(function (cb) {
                try {
                  cb(evt);
                } catch (e) {
                  console.error(e);
                }
              });
            };
          });
          start = Date.now();
          _context4.prev = 5;
          _context4.next = 8;
          return (0, _effects.race)({ timeout: (0, _effects.call)(_reduxSaga.delay, 2000), w: ws });

        case 8:
          _ref3 = _context4.sent;
          timeout = _ref3.timeout;
          w = _ref3.w;
          _context4.next = 23;
          break;

        case 13:
          _context4.prev = 13;
          _context4.t0 = _context4["catch"](5);

          console.error("Failed to start websocket connection", _context4.t0);
          _context4.next = 18;
          return (0, _effects.put)(WSState.Error({
            error: {
              error: "Could not connect to server",
              error_code: "FailedToConnected"
            }
          }));

        case 18:
          diff = Date.now() - start;

          if (!(diff < 1000)) {
            _context4.next = 22;
            break;
          }

          _context4.next = 22;
          return (0, _effects.call)(_reduxSaga.delay, 1000 - diff);

        case 22:
          return _context4.abrupt("return");

        case 23:
          if (!timeout) {
            _context4.next = 27;
            break;
          }

          console.error("timed out waiting for websocket");
          socket.close();
          return _context4.abrupt("return", false);

        case 27:
          _context4.next = 29;
          return (0, _effects.call)(_reduxSaga.channel);

        case 29:
          waiter = _context4.sent;
          _context4.next = 32;
          return (0, _effects.fork)(tickMessages, w);

        case 32:
          ticker = _context4.sent;
          _context4.next = 35;
          return (0, _effects.fork)(sendToSocket, w, sendch, actions);

        case 35:
          sender = _context4.sent;


          oncloses.push(function () {
            waiter.put(_reduxSaga.END);
          });

          _context4.prev = 37;
          _context4.next = 40;
          return (0, _effects.put)(WSState.Connected());

        case 40:
          _context4.next = 42;
          return (0, _effects.take)(waiter);

        case 42:
          _context4.prev = 42;
          _context4.next = 45;
          return (0, _effects.put)(WSState.Error({
            error: { error: "Server went away", error_code: "ServerWentAway" }
          }));

        case 45:
          waiter.close();
          _context4.next = 48;
          return (0, _effects.cancel)(ticker);

        case 48:
          _context4.next = 50;
          return (0, _effects.cancel)(sender);

        case 50:
          return _context4.finish(42);

        case 51:
        case "end":
          return _context4.stop();
      }
    }
  }, _marked4, this, [[5, 13], [37,, 42, 51]]);
}

function processWsSend(commandch, sendch, actions, defaultonerror) {
  var normalise, _ref5, payload, messageId, normalised;

  return regeneratorRuntime.wrap(function processWsSend$(_context5) {
    while (1) {
      switch (_context5.prev = _context5.next) {
        case 0:
          normalise = function normalise(messageId, _ref4) {
            var path = _ref4.path,
                body = _ref4.body,
                onerror = _ref4.onerror,
                onsuccess = _ref4.onsuccess,
                onprogress = _ref4.onprogress,
                original = _ref4.original,
                timeout = _ref4.timeout;

            var done = false;

            var create = function create(cb, msg) {
              try {
                return cb(msg);
              } catch (e) {
                console.error(e);
                try {
                  return defaultonerror({
                    error_code: "INTERNAL_ERROR",
                    error: e.toString()
                  });
                } catch (e2) {
                  console.error(e2);
                }
              }
            };

            var data = { path: path, body: body, message_id: messageId };
            var doerror = function doerror(error) {
              if (done) {
                return;
              }

              done = true;
              if (onerror) {
                return create(onerror, _extends({}, error, { messageId: messageId, original: original }));
              }
            };

            var dosuccess = function dosuccess(data, msgid) {
              if (done) {
                return;
              }

              done = true;
              if (onsuccess) {
                return create(onsuccess, { messageId: messageId, data: data, original: original });
              }
            };

            var doprogress = function doprogress(progress) {
              if (onprogress) {
                return create(onprogress, { messageId: messageId, progress: progress, original: original });
              }
            };

            return {
              data: data,
              messageId: messageId,
              timeout: timeout,
              onsuccess: dosuccess,
              onerror: doerror,
              onprogress: doprogress
            };
          };

        case 1:
          if (false) {}

          _context5.next = 4;
          return (0, _effects.take)(commandch);

        case 4:
          _ref5 = _context5.sent;
          payload = _ref5.payload;
          messageId = (0, _v2.default)();
          normalised = normalise(messageId, payload);

          actions[messageId] = normalised;
          _context5.next = 11;
          return (0, _effects.spawn)(maybeTimeoutMessage, actions, messageId);

        case 11:
          normalised.timeouter = _context5.sent;
          _context5.next = 14;
          return (0, _effects.put)(sendch, normalised);

        case 14:
          _context5.next = 1;
          break;

        case 16:
        case "end":
          return _context5.stop();
      }
    }
  }, _marked5, this);
}

function processWsReceive(receivech, actions) {
  var makeResponse, _ref6, data, action, response;

  return regeneratorRuntime.wrap(function processWsReceive$(_context6) {
    while (1) {
      switch (_context6.prev = _context6.next) {
        case 0:
          makeResponse = function makeResponse(action, data) {
            if (data.reply) {
              if (data.reply.progress) {
                return action.onprogress(data.reply.progress);
              } else if (data.reply.error) {
                return action.onerror(data.reply);
              } else {
                return action.onsuccess(data.reply, data.message_id);
              }
            }

            if (data.error) {
              return action.onerror(data.error);
            }
          };

        case 1:
          if (false) {}

          _context6.next = 4;
          return (0, _effects.take)(receivech);

        case 4:
          _ref6 = _context6.sent;
          data = _ref6.data;
          _context6.prev = 6;

          data = JSON.parse(data);
          _context6.next = 14;
          break;

        case 10:
          _context6.prev = 10;
          _context6.t0 = _context6["catch"](6);

          console.error("failed to parse json from the server", _context6.t0);
          return _context6.abrupt("continue", 1);

        case 14:
          if (data.message_id) {
            _context6.next = 17;
            break;
          }

          console.error("Got a message from the server without a message id", data);
          return _context6.abrupt("continue", 1);

        case 17:
          if (!(data.message_id == "__tick__")) {
            _context6.next = 19;
            break;
          }

          return _context6.abrupt("continue", 1);

        case 19:
          if (!(data.message_id == "__server_time__")) {
            _context6.next = 23;
            break;
          }

          _context6.next = 22;
          return (0, _effects.put)(WSState.ServerTime(data.reply));

        case 22:
          return _context6.abrupt("continue", 1);

        case 23:
          action = actions[data.message_id];

          if (action) {
            _context6.next = 27;
            break;
          }

          console.error("Got a message from the server with unknown message id", data.message_id, data);
          return _context6.abrupt("continue", 1);

        case 27:
          if (!action.timeouter) {
            _context6.next = 30;
            break;
          }

          _context6.next = 30;
          return (0, _effects.cancel)(action.timeouter);

        case 30:
          response = undefined;
          _context6.prev = 31;

          response = makeResponse(action, data);

        case 33:
          _context6.prev = 33;

          if (!response) {
            _context6.next = 37;
            break;
          }

          _context6.next = 37;
          return (0, _effects.put)(response);

        case 37:
          return _context6.finish(33);

        case 38:

          // Finished with this message if not a progress message
          if (response && (!data.reply || !data.reply.progress)) {
            delete actions[data.message_id];
          }
          _context6.next = 1;
          break;

        case 41:
        case "end":
          return _context6.stop();
      }
    }
  }, _marked6, this, [[6, 10], [31,, 33, 38]]);
}

function getWSCommands(commandch) {
  var nxt;
  return regeneratorRuntime.wrap(function getWSCommands$(_context7) {
    while (1) {
      switch (_context7.prev = _context7.next) {
        case 0:
          if (false) {}

          _context7.next = 3;
          return (0, _effects.take)(WSCommand);

        case 3:
          nxt = _context7.sent;
          _context7.next = 6;
          return (0, _effects.put)(commandch, nxt);

        case 6:
          _context7.next = 0;
          break;

        case 8:
        case "end":
          return _context7.stop();
      }
    }
  }, _marked7, this);
}

function listen(url, defaultonerror, delayMS) {
  var count, messages, sendch, receivech, commandch, actions, sendprocess, receiveprocess, ids, i, action, response;
  return regeneratorRuntime.wrap(function listen$(_context8) {
    while (1) {
      switch (_context8.prev = _context8.next) {
        case 0:
          count = 0;
          messages = {};
          _context8.next = 4;
          return (0, _effects.call)(_reduxSaga.channel);

        case 4:
          sendch = _context8.sent;
          _context8.next = 7;
          return (0, _effects.call)(_reduxSaga.channel);

        case 7:
          receivech = _context8.sent;
          _context8.next = 10;
          return (0, _effects.call)(_reduxSaga.channel);

        case 10:
          commandch = _context8.sent;


          if (defaultonerror === undefined) {
            defaultonerror = function defaultonerror(e) {
              return console.error(e);
            };
          }

          // This is outside the while true so that we don't miss messages
          // when the server goes away and before we've started processWsSend again
          _context8.next = 14;
          return (0, _effects.fork)(getWSCommands, commandch);

        case 14:
          if (false) {}

          _context8.next = 17;
          return (0, _effects.put)(WSState.Loading());

        case 17:

          count += 1;
          actions = {};

          messages[count] = actions;
          _context8.next = 22;
          return (0, _effects.fork)(processWsSend, commandch, sendch, actions, defaultonerror);

        case 22:
          sendprocess = _context8.sent;
          _context8.next = 25;
          return (0, _effects.fork)(processWsReceive, receivech, actions);

        case 25:
          receiveprocess = _context8.sent;
          _context8.next = 28;
          return (0, _effects.call)(startWS, url, count, sendch, receivech, actions);

        case 28:
          _context8.next = 30;
          return (0, _effects.cancel)(sendprocess);

        case 30:
          _context8.next = 32;
          return (0, _effects.cancel)(receiveprocess);

        case 32:
          ids = Object.keys(actions);
          i = 0;

        case 34:
          if (!(i < ids.length)) {
            _context8.next = 46;
            break;
          }

          action = actions[ids[i]];

          if (!action.timeouter) {
            _context8.next = 39;
            break;
          }

          _context8.next = 39;
          return (0, _effects.cancel)(action.timeouter);

        case 39:
          response = action.onerror({
            error: "Lost connection to the server",
            error_code: "LostConnection"
          });

          if (!response) {
            _context8.next = 43;
            break;
          }

          _context8.next = 43;
          return (0, _effects.put)(response);

        case 43:
          i++;
          _context8.next = 34;
          break;

        case 46:

          delete messages[count];
          _context8.next = 49;
          return (0, _effects.call)(_reduxSaga.delay, delayMS || 5000);

        case 49:
          _context8.next = 14;
          break;

        case 51:
        case "end":
          return _context8.stop();
      }
    }
  }, _marked8, this);
}

/***/ }),

/***/ 0:
/*!******************************************!*\
  !*** multi ./js/index.js ./css/app.scss ***!
  \******************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(/*! ./js/index.js */"./js/index.js");
module.exports = __webpack_require__(/*! ./css/app.scss */"./css/app.scss");


/***/ })

/******/ });
//# sourceMappingURL=app.js.map