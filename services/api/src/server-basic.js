const express = require('express');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');

// Load environment variables
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env') });

const app = express();
const port = process.env.PORT || 8080;

console.log('🚀 Starting TrustNet API in basic development mode...');

// Basic middleware
app.use(cors());
app.use(express.json());

// Simple logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  console.log('✅ Health check requested');
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0-dev',
    mode: 'basic_development',
    features: {
      verification_engine: true,
      quarantine_room: true,
      proactive_feed: true
    }
  });
});

// Basic info endpoint
app.get('/', (req, res) => {
  console.log('📚 API info requested');
  res.json({
    name: 'TrustNet API',
    description: 'AI-powered misinformation detection system for India',
    version: '1.0.0-dev',
    status: 'Development Mode - Basic Functionality',
    endpoints: [
      'GET /health - Health check',
      'GET / - API information',
      'POST /v1/verify - Verify content',
      'GET /v1/verify/:id - Get verification results',
      'POST /v1/feedback - Submit feedback'
    ]
  });
});

// Core verification endpoint
app.post('/v1/verify', (req, res) => {
  try {
    const { text, urls = [], language = 'en' } = req.body;
    
    if (!text) {
      return res.status(400).json({
        error: 'Missing text',
        message: 'Text field is required'
      });
    }

    const verificationId = uuidv4();
    
    console.log(`🔍 Processing verification request: ${verificationId}`);
    console.log(`📝 Text (first 100 chars): ${text.substring(0, 100)}${text.length > 100 ? '...' : ''}`);

    // Mock response for development
    res.status(202).json({
      verification_id: verificationId,
      status: 'analyzing',
      message: 'Content analysis in progress (DEVELOPMENT MODE)',
      text_preview: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
      check_url: `/v1/verify/${verificationId}`,
      estimated_completion: new Date(Date.now() + 5000).toISOString()
    });

  } catch (error) {
    console.error('❌ Verification request failed:', error.message);
    res.status(500).json({
      error: 'Analysis failed',
      message: error.message
    });
  }
});

// Get verification results (mock)
app.get('/v1/verify/:verificationId', (req, res) => {
  const { verificationId } = req.params;
  
  console.log(`📊 Retrieving verification results: ${verificationId}`);

  // Mock successful analysis result
  const mockResult = {
    verification_id: verificationId,
    status: 'completed',
    analysis_result: {
      credibility_score: 0.75,
      rating: 'partially_verified', 
      confidence: 0.8,
      summary: 'This content has been analyzed using our AI detection algorithms.',
      sources_checked: 3,
      manipulation_indicators: [
        {
          type: 'emotional_language',
          severity: 'low',
          description: 'Contains emotionally charged words'
        }
      ],
      recommendations: [
        'Verify with additional sources',
        'Check publication date and context',
        'Look for expert opinions on this topic'
      ]
    },
    processing_time: 2500,
    completed_at: new Date().toISOString(),
    note: 'This is a mock response for development testing'
  };

  res.json(mockResult);
});

// Feedback endpoint
app.post('/v1/feedback', (req, res) => {
  try {
    const feedbackId = uuidv4();
    const { verdict_id, rating, comments } = req.body;

    console.log(`💬 Feedback received: ${feedbackId} - Rating: ${rating}`);

    res.status(201).json({
      feedback_id: feedbackId,
      message: 'Thank you for your feedback!',
      note: 'Feedback stored in development mode'
    });
  } catch (error) {
    res.status(500).json({
      error: 'Feedback submission failed',
      message: error.message
    });
  }
});

// 404 handler
app.use((req, res) => {
  console.log(`❓ Unknown endpoint requested: ${req.method} ${req.path}`);
  res.status(404).json({
    error: 'Endpoint not found',
    message: `${req.method} ${req.path} is not available`,
    available_endpoints: [
      'GET /',
      'GET /health', 
      'POST /v1/verify',
      'GET /v1/verify/:id',
      'POST /v1/feedback'
    ]
  });
});

// Start server
const server = app.listen(port, () => {
  console.log('\n🎉 TrustNet API Server Started Successfully!');
  console.log('==========================================');
  console.log(`🚀 Server running on: http://localhost:${port}`);
  console.log(`🏥 Health check: http://localhost:${port}/health`);
  console.log(`📚 API info: http://localhost:${port}/`);
  console.log(`🔧 Mode: Basic Development`);
  console.log(`📅 Started at: ${new Date().toISOString()}`);
  console.log('==========================================\n');
  console.log('📝 Press Ctrl+C to stop the server');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down TrustNet server...');
  server.close(() => {
    console.log('✅ Server shut down gracefully');
    process.exit(0);
  });
});

// Handle server errors
server.on('error', (error) => {
  if (error.code === 'EADDRINUSE') {
    console.error(`❌ Port ${port} is already in use. Please choose a different port.`);
    process.exit(1);
  } else {
    console.error('❌ Server error:', error);
    process.exit(1);
  }
});

module.exports = app;
