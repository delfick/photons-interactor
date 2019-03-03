const MiniCssExtractPlugin = require("mini-css-extract-plugin");
var webpack = require("webpack");
var path = require("path");

var mode = process.env.NODE_ENV || "development";

module.exports = {
  mode: mode,
  entry: ["./js/index.js"],
  output: {
    filename: "static/app.js",
    path: path.resolve(__dirname, "dist")
  },
  optimization: {
    splitChunks: {
      chunks: "all"
    }
  },
  devtool: "eval-source-map",
  plugins: [
    new MiniCssExtractPlugin({
      filename: "static/[name].css"
    }),
    new webpack.DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify(mode)
    }),
    new webpack.ProvidePlugin({ React: "react" })
  ],
  module: {
    rules: [
      {
        test: /\.(sa|sc|c)ss$/,
        use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"]
      },
      {
        test: /\.woff2?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        use: "url-loader"
      },
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: ["@babel/preset-env", "@babel/preset-react"],
              plugins: [
                ["@babel/plugin-proposal-decorators", { legacy: true }],
                "@babel/transform-runtime",
                "@babel/plugin-proposal-class-properties"
              ]
            }
          }
        ]
      }
    ]
  }
};
