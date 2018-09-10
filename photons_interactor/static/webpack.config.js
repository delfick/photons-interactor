var ExtractTextPlugin = require("extract-text-webpack-plugin");
var webpack = require("webpack");
var path = require("path");

const NODE_ENV = process.env.NODE_ENV || "development";

var plugins = [
  new ExtractTextPlugin({ filename: "static/app.css" }),
  new webpack.DefinePlugin({
    "process.env.NODE_ENV": JSON.stringify(NODE_ENV)
  }),
  new webpack.ProvidePlugin({ React: "react" })
];

module.exports = {
  entry: ["./js/index.js", "./css/app.scss"],
  mode: NODE_ENV,
  devtool: "eval-source-map",
  output: { filename: "static/app.js", path: path.resolve(__dirname, "dist") },
  plugins: plugins,
  resolve: { symlinks: false },
  optimization: {
    namedChunks: true,
    splitChunks: {
      cacheGroups: {
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: "vendor",
          chunks: "all",
          enforce: true
        }
      }
    }
  },
  module: {
    rules: [
      {
        test: /.s?css$/,
        use: ExtractTextPlugin.extract({
          use: [{ loader: "css-loader" }, { loader: "sass-loader" }]
        })
      },
      {
        test: /\.woff2?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        use: "url-loader"
      },
      {
        test: /.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["env", "react"],
            plugins: [
              "transform-object-rest-spread",
              "syntax-export-extensions",
              "transform-decorators-legacy",
              "transform-function-bind",
              "transform-class-properties",
              "transform-es2015-template-literals"
            ]
          }
        }
      }
    ]
  }
};
