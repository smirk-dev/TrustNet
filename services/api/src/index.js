const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const { v4: uuidv4 } = require('uuid');
const Joi = require('joi');

const { Firestore } = require('@google-cloud/firestore');
const { PubSub } = require('@google-cloud/pubsub');
const { DlpServiceClient } = require('@google-cloud/dlp');

const logger = require('./utils/logger');
const { validateAnalysisRequest } = require('./middleware/validation');
const { authMiddleware } = require('./middleware/auth');
const { rateLimitMiddleware } = require('./middleware/rateLimit');

const app = express();
const port = process.env.PORT || 8080;

// Initialize Google Cloud services
const firestore = new Firestore();
const pubsub = new PubSub();
const dlp = new DlpServiceClient();

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.SERVICE_VERSION || '1.0.0'
  });
});

// Submit content for analysis
app.post('/v1/analyze', 
  rateLimitMiddleware,
  validateAnalysisRequest,
  async (req, res) => {
    try {
      const claimId = uuidv4();
      const { text, urls = [], language = 'en', priority = 'normal' } = req.body;

      // Create claim record
      const claim = {
        id: claimId,
        text,
        urls,
        language,
        source_type: req.body.source_type || 'web',
        user_segment: req.body.user_segment || 'citizen',
        created_at: new Date().toISOString(),
        status: 'pending',
        pii_redacted: false
      };

      // Store in Firestore
      await firestore.collection('claims').doc(claimId).set(claim);

      // Publish to analysis pipeline
      const message = {
        claim_id: claimId,
        text,
        urls,
        language,
        priority
      };

      const topic = pubsub.topic('content-analysis');
      await topic.publishMessage({
        data: Buffer.from(JSON.stringify(message)),
        attributes: {
          claimId,
          language,
          priority
        }
      });

      logger.info('Analysis request submitted', { claimId, language, priority });

      if (priority === 'high') {
        // Wait for quick synchronous processing
        // TODO: Implement real-time processing for high priority
        res.status(202).json({
          claim_id: claimId,
          status: 'processing',
          estimated_completion: new Date(Date.now() + 30000).toISOString()
        });
      } else {
        res.status(202).json({
          claim_id: claimId,
          status: 'queued',
          estimated_completion: new Date(Date.now() + 120000).toISOString()
        });
      }

    } catch (error) {
      logger.error('Analysis request failed', { error: error.message });
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to process analysis request'
      });
    }
  }
);

// Get claim analysis results
app.get('/v1/claims/:claimId', async (req, res) => {
  try {
    const { claimId } = req.params;

    const claimDoc = await firestore.collection('claims').doc(claimId).get();
    if (!claimDoc.exists) {
      return res.status(404).json({
        error: 'Claim not found',
        claim_id: claimId
      });
    }

    const claim = claimDoc.data();

    // Get verdict if available
    const verdictDoc = await firestore.collection('verdicts')
      .where('claim_id', '==', claimId)
      .orderBy('created_at', 'desc')
      .limit(1)
      .get();

    if (verdictDoc.empty) {
      return res.json({
        claim_id: claimId,
        status: claim.status,
        claim: claim,
        processing: true
      });
    }

    const verdict = verdictDoc.docs[0].data();

    // Get evidence
    const evidenceQuery = await firestore.collection('evidence')
      .where('claim_id', '==', claimId)
      .orderBy('relevance_score', 'desc')
      .limit(5)
      .get();

    const evidence = evidenceQuery.docs.map(doc => doc.data());

    res.json({
      claim_id: claimId,
      status: 'completed',
      claim,
      verdict,
      evidence,
      processing_completed_at: verdict.created_at
    });

  } catch (error) {
    logger.error('Failed to retrieve claim', { error: error.message, claimId: req.params.claimId });
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to retrieve claim analysis'
    });
  }
});

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

    await firestore.collection('feedback').doc(feedbackId).set(feedback);

    logger.info('Feedback submitted', { feedbackId, verdictId: feedback.verdict_id });

    res.status(201).json({
      feedback_id: feedbackId,
      message: 'Feedback recorded successfully'
    });

  } catch (error) {
    logger.error('Failed to submit feedback', { error: error.message });
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
    message: 'The requested endpoint does not exist'
  });
});

app.listen(port, () => {
  logger.info(`TrustNet API server running on port ${port}`);
});

module.exports = app;
