const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://127.0.0.1:8001',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug',
      onError: function (err, req, res) {
        console.log('Proxy Error:', err);
      }
    })
  );

  app.use(
    '/health',
    createProxyMiddleware({
      target: 'http://127.0.0.1:8001',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug'
    })
  );
};
