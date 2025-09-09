console.log('🚀 Simple Node.js test starting...');
console.log('Node.js version:', process.version);
console.log('Platform:', process.platform);
console.log('Current working directory:', process.cwd());

try {
  const express = require('express');
  console.log('✅ Express loaded successfully');
  
  const app = express();
  const port = 8080;
  
  app.get('/test', (req, res) => {
    res.json({ message: 'Simple test works!', timestamp: new Date() });
  });
  
  const server = app.listen(port, () => {
    console.log(`✅ Simple server running on http://localhost:${port}/test`);
  });
  
  // Keep the server running
  process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down server...');
    server.close(() => {
      console.log('Server closed');
      process.exit(0);
    });
  });
  
} catch (error) {
  console.error('❌ Error:', error.message);
  process.exit(1);
}
