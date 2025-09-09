const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const { v4: uuidv4 } = require('uuid');

// Load environment variables
require('dotenv').config();

const logger = require('./utils/logger');

const app = express();
const port = process.env.PORT || 8080;

// Development mode check
const isDevelopment = process.env.DEVELOPMENT_MODE === 'true';
const mockServices = process.env.MOCK_GOOGLE_SERVICES === 'true';

// Mock Google Cloud services for development
let firestore, pubsub, dlp;

if (mockServices && isDevelopment) {
  // Mock implementations for development
  firestore = {
    collection: () => ({
      doc: () => ({
        set: async () => ({ writeTime: new Date() }),
        get: async () => ({ exists: false }),
        update: async () => ({ writeTime: new Date() })
      }),
      where: () => ({
        orderBy: () => ({
          limit: () => ({
            get: async () => ({ empty: true, docs: [] })
          })
        })
      })
    })
  };
  
  pubsub = {
    topic: () => ({
      publishMessage: async () => ({ messageId: 'mock-' + uuidv4() })
    })
  };
  
  dlp = {
    inspectContent: async () => ({ findings: [] })
  };
  
  console.log('🚀 Running in DEVELOPMENT MODE with mocked Google Cloud services');
} else {
  // Real Google Cloud services
  const { Firestore } = require('@google-cloud/firestore');
  const { PubSub } = require('@google-cloud/pubsub');
  const { DlpServiceClient } = require('@google-cloud/dlp');
  
  firestore = new Firestore();
  pubsub = new PubSub();
  dlp = new DlpServiceClient();
}

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Basic rate limiting middleware (simplified for development)
const rateLimitStore = new Map();
const rateLimitMiddleware = (req, res, next) => {
  if (!isDevelopment) {
    // Implement proper rate limiting in production
    const clientIP = req.ip;
    const now = Date.now();
    const windowMs = 15 * 60 * 1000; // 15 minutes
    const limit = parseInt(process.env.API_RATE_LIMIT) || 100;
    
    if (!rateLimitStore.has(clientIP)) {
      rateLimitStore.set(clientIP, { count: 1, resetTime: now + windowMs });
    } else {
      const clientData = rateLimitStore.get(clientIP);
      if (now > clientData.resetTime) {
        rateLimitStore.set(clientIP, { count: 1, resetTime: now + windowMs });
      } else {
        clientData.count++;
        if (clientData.count > limit) {
          return res.status(429).json({
            error: 'Too many requests',
            message: `Rate limit exceeded. Try again in ${Math.ceil((clientData.resetTime - now) / 1000)} seconds.`
          });
        }
      }
    }
  }
  next();
};

// Basic validation middleware
const validateAnalysisRequest = (req, res, next) => {
  const { text } = req.body;
  
  if (!text || typeof text !== 'string') {
    return res.status(400).json({
      error: 'Invalid request',
      message: 'Text field is required and must be a string'
    });
  }
  
  if (text.length > 10000) {
    return res.status(400).json({
      error: 'Text too long',
      message: 'Text must be less than 10,000 characters'
    });
  }
  
  next();
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.SERVICE_VERSION || '1.0.0',
    mode: isDevelopment ? 'development' : 'production',
    features: {
      verification_engine: true,
      quarantine_room: true,
      proactive_feed: true,
      no_login_required: true
    },
    services: {
      firestore: mockServices ? 'mocked' : 'connected',
      pubsub: mockServices ? 'mocked' : 'connected',
      dlp: mockServices ? 'mocked' : 'connected'
    }
  });
});

// Basic info endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'TrustNet API',
    description: 'AI-powered misinformation detection system for India',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      verify: 'POST /v1/verify',
      verification_status: 'GET /v1/verify/:verificationId',
      quarantine: 'GET /v1/quarantine/:verificationId',
      submit_verdict: 'POST /v1/quarantine/:verificationId/verdict',
      analyze: 'POST /v1/analyze',
      feedback: 'POST /v1/feedback'
    },
    documentation: 'https://github.com/smirk-dev/TrustNet'
  });
});

// Verification Engine - Core MVP Feature
app.post('/v1/verify', 
  rateLimitMiddleware,
  validateAnalysisRequest,
  async (req, res) => {
    try {
      const verificationId = uuidv4();
      const { text, urls = [], language = 'en', source_type = 'web' } = req.body;

      console.log(`📝 Processing verification request: ${verificationId}`);

      // Create verification request (mocked for development)
      const verification = {
        id: verificationId,
        text: text.substring(0, 200) + (text.length > 200 ? '...' : ''),
        urls,
        language,
        source_type,
        created_at: new Date().toISOString(),
        status: 'analyzing',
        user_ip: req.ip
      };

      // Store request (mocked)
      if (mockServices) {
        console.log('💾 Storing verification request (mocked):', verification);
      } else {
        await firestore.collection('verifications').doc(verificationId).set(verification);
      }

      // Trigger analysis pipeline (mocked)
      const message = {
        verification_id: verificationId,
        text,
        urls,
        language,
        analysis_type: 'verification_engine'
      };

      if (mockServices) {
        console.log('📨 Publishing to analysis queue (mocked):', { verificationId, language });
      } else {
        const topic = pubsub.topic('verification-analysis');
        await topic.publishMessage({
          data: Buffer.from(JSON.stringify(message)),
          attributes: { verificationId, language }
        });
      }

      logger.info('Verification request submitted', { verificationId, language });

      // Return immediate response for MVP
      res.status(202).json({
        verification_id: verificationId,
        status: 'analyzing',
        message: 'Content analysis in progress',
        check_url: `/v1/verify/${verificationId}`,
        estimated_completion: new Date(Date.now() + 30000).toISOString(),
        development_note: mockServices ? 'Running with mocked services for development' : undefined
      });

    } catch (error) {
      logger.error('Verification request failed', { error: error.message });
      res.status(500).json({
        error: 'Analysis failed',
        message: 'Unable to process verification request'
      });
    }
  }
);

// Get verification results (mocked response for development)
app.get('/v1/verify/:verificationId', async (req, res) => {
  try {
    const { verificationId } = req.params;

    console.log(`🔍 Retrieving verification: ${verificationId}`);

    if (mockServices) {
      // Return a mocked successful verification response
      const mockResult = {
        verification_id: verificationId,
        status: 'completed',
        verification_card: {
          credibility_score: 0.75,
          rating: 'partially_verified',
          confidence: 0.8,
          source_analysis: {
            sources_found: 3,
            credible_sources: 2,
            contradicting_sources: 1
          },
          alternative_headlines: [
            "Similar claim found with additional context",
            "Fact-checkers report mixed evidence on this topic"
          ],
          neutral_summary: "This claim contains elements that are partially accurate but lacks important context.",
          manipulation_alerts: [
            {
              type: 'emotional_language',
              severity: 'medium',
              description: 'Content uses emotionally charged language'
            }
          ],
          education_tips: [
            "Look for multiple credible sources when evaluating claims",
            "Be cautious of content that uses urgent or emotional language",
            "Check the publication date and context of information"
          ]
        },
        processing_time: 2340,
        completed_at: new Date().toISOString(),
        development_note: 'This is a mocked response for development testing'
      };

      // Simulate some processing delay
      setTimeout(() => {
        res.json(mockResult);
      }, 1000);
    } else {
      // Real implementation would query Firestore
      res.json({
        verification_id: verificationId,
        status: 'processing',
        message: 'Analysis still in progress',
        progress: 60
      });
    }

  } catch (error) {
    logger.error('Failed to retrieve verification', { 
      error: error.message, 
      verificationId: req.params.verificationId 
    });
    res.status(500).json({
      error: 'Retrieval failed',
      message: 'Unable to get verification results'
    });
  }
});

// Legacy analyze endpoint (for backward compatibility)
app.post('/v1/analyze', 
  rateLimitMiddleware,
  validateAnalysisRequest,
  async (req, res) => {
    const claimId = uuidv4();
    const { text, urls = [], language = 'en', priority = 'normal' } = req.body;

    console.log(`📊 Processing legacy analyze request: ${claimId}`);

    try {
      if (mockServices) {
        console.log('💾 Storing claim (mocked):', { claimId, text: text.substring(0, 100) + '...' });
      }

      res.status(202).json({
        claim_id: claimId,
        status: priority === 'high' ? 'processing' : 'queued',
        estimated_completion: new Date(Date.now() + (priority === 'high' ? 30000 : 120000)).toISOString(),
        development_note: mockServices ? 'Running with mocked services' : undefined
      });
    } catch (error) {
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to process analysis request'
      });
    }
  }
);

// Submit feedback
app.post('/v1/feedback', async (req, res) => {
  try {
    const feedbackId = uuidv4();
    const feedback = {
      id: feedbackId,
      verdict_id: req.body.verdict_id,
      user_rating: req.body.user_rating,
      feedback_type: req.body.feedback_type,
      comments: req.body.comments || '',
      user_expertise: req.body.user_expertise || 'general_public',
      created_at: new Date().toISOString()
    };

    console.log('💬 Feedback submitted:', { feedbackId, rating: feedback.user_rating });

    if (mockServices) {
      console.log('💾 Storing feedback (mocked):', feedback);
    }

    res.status(201).json({
      feedback_id: feedbackId,
      message: 'Feedback recorded successfully',
      development_note: mockServices ? 'Feedback stored in development mode' : undefined
    });

  } catch (error) {
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to record feedback'
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error', { error: err.message, stack: err.stack });
  res.status(500).json({
    error: 'Internal server error',
    message: 'An unexpected error occurred'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    message: 'The requested endpoint does not exist',
    available_endpoints: [
      'GET /',
      'GET /health',
      'POST /v1/verify',
      'GET /v1/verify/:id',
      'POST /v1/analyze',
      'POST /v1/feedback'
    ]
  });
});

app.listen(port, () => {
  console.log(`🚀 TrustNet API server running on port ${port}`);
  console.log(`📍 Base URL: http://localhost:${port}`);
  console.log(`🏥 Health check: http://localhost:${port}/health`);
  console.log(`📚 API info: http://localhost:${port}/`);
  console.log(`🔧 Mode: ${isDevelopment ? 'DEVELOPMENT' : 'PRODUCTION'}`);
  console.log(`☁️  Google Cloud services: ${mockServices ? 'MOCKED' : 'CONNECTED'}`);
  
  logger.info(`TrustNet API server running on port ${port}`);
});

module.exports = app;
