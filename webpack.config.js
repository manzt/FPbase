const path = require('path');
const webpack = require('webpack');
const autoprefixer = require('autoprefixer');

const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const BundleTracker = require('webpack-bundle-tracker');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ImageminWebpackPlugin = require("imagemin-webpack-plugin").default;
const ImageminWebP = require("imagemin-webp");
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const SentryCliPlugin = require('@sentry/webpack-plugin');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');
//const { VueLoaderPlugin } = require('vue-loader');

const devMode = process.env.NODE_ENV !== 'production';
const hotReload = process.env.HOT_RELOAD === '1';

//const vueRule = {
//  test: /\.vue$/,
//  use: 'vue-loader',
//  exclude: /node_modules/
//};

const styleRule = {
  test: /\.(sa|sc|c)ss$/,
  use: [
    MiniCssExtractPlugin.loader,
    { loader: 'css-loader', options: { sourceMap: true } },
    {
      loader: 'postcss-loader',
      options: {
        plugins: () => [
          autoprefixer({ browsers: ['last 2 versions'] }),
          require('cssnano')
        ],
      },
    },
    'sass-loader',
  ]
};

const jsRule = {
  test: /\.jsx?$/,
  //exclude: /node_modules/,
  use: {
    loader: 'babel-loader',
    options: {
      presets: ['@babel/preset-env', '@babel/preset-react'],
      plugins: ["@babel/plugin-syntax-dynamic-import"],
    }
  }
};

const assetRule = {
  test: /.(jpg|png|woff(2)?|eot|ttf|svg)$/,
  loader: 'file-loader'
};

const plugins = [
  new webpack.ProvidePlugin({
    $: 'jquery',
    jQuery: 'jquery'
  }),
  new webpack.IgnorePlugin(/vertx/),
  new BundleTracker({ filename: './webpack-stats.json' }),
  //new VueLoaderPlugin(),
  new MiniCssExtractPlugin({
    filename: '[name].css',
    chunkFilename: '[id].css'
  }),
  new BundleAnalyzerPlugin({ analyzerMode: 'static', openAnalyzer: false }),
  new webpack.HotModuleReplacementPlugin(),
  new CleanWebpackPlugin(['./static/dist']),
  new CopyWebpackPlugin([
      {
          from: './static/src/images/**/*',
          to: path.resolve('./static/dist/images/[name].webp'),
          toType: 'template',
      },
  ]),
  new ImageminWebpackPlugin({
      test: /\.(webp)$/i,
      plugins: [
          ImageminWebP({
              quality: 90,
              sharpness: 1,
          }),
      ],
  }),
  new CopyWebpackPlugin([
      {
          from: './static/src/images/**/*',
          to: path.resolve('./static/dist/images/[name].[ext]'),
          toType: 'template',
      },
  ]),
];

if (devMode) {
  styleRule.use = ['css-hot-loader', ...styleRule.use];
} else {
  plugins.push(
    new webpack.EnvironmentPlugin({
      NODE_ENV: 'development',
      SOURCE_VERSION: false,
      SENTRY_DSN: false,
      SENTRY_AUTH_TOKEN: false,
    })
  );

  if (process.env.SENTRY_AUTH_TOKEN && !process.env.CI) {
    plugins.push(
      new SentryCliPlugin({
        include: 'static/',
        release: process.env.SOURCE_VERSION,
        ignore: ['node_modules', 'webpack.config.js'],
      })
    );
  }
}

module.exports = {
  context: __dirname,
  entry: {
    main: './static/src/index.js',
    embedscope: './static/src/embedscope.js',
    litemol: './static/src/my-litemol.js'
  },
  output: {
    path: path.resolve('./static/dist/'),
    filename: '[name].js',
    publicPath: hotReload ? 'http://localhost:8080/static/' : '/static/',
    chunkFilename: '[name]-bundle.js',
  },
  resolve: {
      alias: {
          jquery: "jquery/src/jquery"
      }
  },
  devtool: devMode ? 'cheap-eval-source-map' : 'source-map',
  devServer: {
    hot: true,
    quiet: false,
    headers: { 'Access-Control-Allow-Origin': '*' }
  },
  module: { rules: [jsRule, styleRule, assetRule] },
  externals: { Sentry: 'Sentry' },
  plugins: plugins,
  optimization: {
    minimizer: [
      new UglifyJsPlugin({
        cache: true,
        parallel: true,
        sourceMap: true // set to true if you want JS source maps
      }),
      new OptimizeCSSAssetsPlugin({})
    ],
    splitChunks: {
      cacheGroups: {
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendor',
          chunks: 'initial',
        },
      }
    }
  },
};
