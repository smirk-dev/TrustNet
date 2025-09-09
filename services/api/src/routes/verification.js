const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { Firestore } = require('@google-cloud/firestore');
const { PubSub } = require('@google-cloud/pubsub');

const { validateAnalysisRequest } = require('../middleware/validation');
const { rateLimitMiddleware } = require('../middleware/rateLimit');
const logger = require('../utils/logger');

const router = express.Router();
const firestore = new Firestore();
const pubsub = new PubSub();

// Automated Verification Engine - Core MVP Feature
router.post('/verify', 
  rateLimitMiddleware,
  validateAnalysisRequest,
  async (req, res) => {
    try {
      const verificationId = uuidv4();
      const { text, urls = [], language = 'en', source_type = 'web' } = req.body;

      // Create verification request
      const verification = {
        id: verificationId,
        text,
        urls,
        language,
        source_type,
        created_at: new Date().toISOString(),
        status: 'analyzing',
        user_ip: req.ip
      };

      // Store request
      await firestore.collection('verifications').doc(verificationId).set(verification);

      // Trigger analysis pipeline
      const message = {
        verification_id: verificationId,
        text,
        urls,
        language,
        analysis_type: 'verification_engine'
      };

      const topic = pubsub.topic('verification-analysis');
      await topic.publishMessage({
        data: Buffer.from(JSON.stringify(message)),
        attributes: { verificationId, language }
      });

      logger.info('Verification request submitted', { verificationId, language });

      // Return immediate response for MVP (no login required)
      res.status(202).json({
        verification_id: verificationId,
        status: 'analyzing',
        message: 'Content analysis in progress',
        check_url: `/v1/verification/${verificationId}`,
        estimated_completion: new Date(Date.now() + 30000).toISOString()
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

// Get verification results
router.get('/verify/:verificationId', async (req, res) => {
  try {
    const { verificationId } = req.params;

    // Get verification request
    const verificationDoc = await firestore.collection('verifications').doc(verificationId).get();
    if (!verificationDoc.exists) {
      return res.status(404).json({
        error: 'Verification not found',
        verification_id: verificationId
      });
    }

    const verification = verificationDoc.data();

    // Get analysis results
    const resultsQuery = await firestore.collection('verification_results')
      .where('verification_id', '==', verificationId)
      .orderBy('created_at', 'desc')
      .limit(1)
      .get();

    if (resultsQuery.empty) {
      return res.json({
        verification_id: verificationId,
        status: verification.status,
        message: 'Analysis still in progress',
        progress: getAnalysisProgress(verification.created_at)
      });
    }

    const result = resultsQuery.docs[0].data();

    // Determine if content needs quarantine
    const needsQuarantine = shouldQuarantine(result);

    if (needsQuarantine) {
      // Move to quarantine room
      await createQuarantineItem(verificationId, result);
      
      return res.json({
        verification_id: verificationId,
        status: 'needs_review',
        quarantine_url: `/v1/quarantine/${verificationId}`,
        confidence_score: result.confidence_score,
        suspicious_indicators: result.suspicious_indicators,
        message: 'Content requires human judgment - moved to Quarantine Room'
      });
    }

    // Return verification card for confident results
    res.json({
      verification_id: verificationId,
      status: 'completed',
      verification_card: {
        credibility_score: result.credibility_score,
        rating: result.rating,
        confidence: result.confidence_score,
        source_analysis: result.source_analysis,
        alternative_headlines: result.alternative_headlines,
        neutral_summary: result.neutral_summary,
        manipulation_alerts: result.manipulation_alerts,
        education_tips: result.education_tips
      },
      processing_time: result.processing_time_ms,
      completed_at: result.created_at
    });

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

// Quarantine Room - Handle uncertain content
router.get('/quarantine/:verificationId', async (req, res) => {
  try {
    const { verificationId } = req.params;

    const quarantineDoc = await firestore.collection('quarantine_items').doc(verificationId).get();
    if (!quarantineDoc.exists) {
      return res.status(404).json({
        error: 'Quarantine item not found'
      });
    }

    const quarantineItem = quarantineDoc.data();

    res.json({
      verification_id: verificationId,
      quarantine_item: {
        original_content: quarantineItem.original_content,
        suspicious_elements: quarantineItem.suspicious_elements,
        ai_uncertainty: quarantineItem.ai_uncertainty,
        highlighted_areas: quarantineItem.highlighted_areas,
        context_needed: quarantineItem.context_needed,
        similar_claims: quarantineItem.similar_claims
      },
      user_action_required: true,
      verdict_options: ['legit', 'misleading', 'needs_more_info'],
      educational_context: quarantineItem.educational_context
    });

  } catch (error) {
    logger.error('Failed to retrieve quarantine item', { error: error.message });
    res.status(500).json({
      error: 'Quarantine retrieval failed'
    });
  }
});

// Submit user verdict from Quarantine Room
router.post('/quarantine/:verificationId/verdict', async (req, res) => {
  try {
    const { verificationId } = req.params;
    const { user_verdict, confidence, reasoning, user_expertise = 'general' } = req.body;

    if (!['legit', 'misleading', 'needs_more_info'].includes(user_verdict)) {
      return res.status(400).json({
        error: 'Invalid verdict',
        message: 'Verdict must be legit, misleading, or needs_more_info'
      });
    }

    const verdictId = uuidv4();
    const verdict = {
      id: verdictId,
      verification_id: verificationId,
      user_verdict,
      user_confidence: confidence,
      user_reasoning: reasoning,
      user_expertise,
      user_ip: req.ip,
      created_at: new Date().toISOString()
    };

    // Store user verdict
    await firestore.collection('user_verdicts').doc(verdictId).set(verdict);

    // Update quarantine status
    await firestore.collection('quarantine_items').doc(verificationId).update({
      status: 'resolved',
      final_verdict: user_verdict,
      resolved_at: new Date().toISOString()
    });

    // Trigger model retraining pipeline with user feedback
    const retrainingTopic = pubsub.topic('user-feedback-training');
    await retrainingTopic.publishMessage({
      data: Buffer.from(JSON.stringify({
        verification_id: verificationId,
        user_verdict,
        ai_confidence: (await getOriginalAIConfidence(verificationId))
      }))
    });

    logger.info('User verdict submitted', { verificationId, verdict: user_verdict });

    res.json({
      verdict_id: verdictId,
      message: 'Thank you for your judgment! This helps improve our AI.',
      contribution_impact: 'Your input will help train better detection models',
      quarantine_resolved: true
    });

  } catch (error) {
    logger.error('Failed to submit verdict', { error: error.message });
    res.status(500).json({
      error: 'Verdict submission failed'
    });
  }
});

// Helper functions
function getAnalysisProgress(createdAt) {
  const elapsed = Date.now() - new Date(createdAt).getTime();
  const totalExpected = 30000; // 30 seconds
  return Math.min(Math.round((elapsed / totalExpected) * 100), 95);
}

function shouldQuarantine(result) {
  // Quarantine if AI confidence is low or conflicting signals detected
  return result.confidence_score < 0.7 || 
         result.conflicting_evidence_score > 0.5 ||
         result.manipulation_uncertainty > 0.6;
}

async function createQuarantineItem(verificationId, result) {
  const quarantineItem = {
    verification_id: verificationId,
    original_content: result.original_text,
    suspicious_elements: result.suspicious_indicators,
    ai_uncertainty: result.confidence_score,
    highlighted_areas: result.visual_highlights,
    context_needed: result.missing_context,
    similar_claims: result.related_claims,
    educational_context: result.pattern_education,
    status: 'pending_review',
    created_at: new Date().toISOString()
  };

  await firestore.collection('quarantine_items').doc(verificationId).set(quarantineItem);
}

async function getOriginalAIConfidence(verificationId) {
  const resultDoc = await firestore.collection('verification_results')
    .where('verification_id', '==', verificationId)
    .limit(1)
    .get();
  
  return resultDoc.empty ? 0.5 : resultDoc.docs[0].data().confidence_score;
}

module.exports = router;
