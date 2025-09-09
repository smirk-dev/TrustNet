const express = require('express');
const { Firestore } = require('@google-cloud/firestore');
const { PubSub } = require('@google-cloud/pubsub');

const logger = require('../utils/logger');

const router = express.Router();
const firestore = new Firestore();

// Proactive Homepage Feed - MVP Priority #3
router.get('/feed', async (req, res) => {
  try {
    const { language = 'en', limit = 10, offset = 0 } = req.query;

    // Get curated educational content
    const feedQuery = firestore.collection('educational_feed')
      .where('status', '==', 'published')
      .where('languages', 'array-contains', language)
      .orderBy('priority_score', 'desc')
      .orderBy('published_at', 'desc')
      .offset(parseInt(offset))
      .limit(parseInt(limit));

    const feedSnapshot = await feedQuery.get();
    
    if (feedSnapshot.empty) {
      return res.json({
        feed_items: [],
        total_count: 0,
        message: 'No content available for this language'
      });
    }

    const feedItems = feedSnapshot.docs.map(doc => {
      const data = doc.data();
      return {
        id: data.id,
        title: data.title,
        type: data.content_type, // 'verified_example', 'debunked_example', 'education_tip'
        summary: data.summary,
        original_claim: data.original_claim,
        verdict: data.verdict,
        evidence_summary: data.evidence_summary,
        learning_points: data.learning_points,
        visual_elements: data.visual_elements,
        engagement_score: data.engagement_score,
        published_at: data.published_at,
        source_attribution: data.source_attribution,
        category: data.category // 'health', 'politics', 'finance', 'social'
      };
    });

    // Get trending topics for context
    const trendingTopics = await getTrendingTopics(language);

    res.json({
      feed_items: feedItems,
      trending_topics: trendingTopics,
      total_count: feedItems.length,
      language: language,
      last_updated: new Date().toISOString(),
      feed_metadata: {
        user_education_focus: true,
        real_world_examples: true,
        proactive_learning: true
      }
    });

  } catch (error) {
    logger.error('Failed to retrieve homepage feed', { error: error.message });
    res.status(500).json({
      error: 'Feed retrieval failed',
      message: 'Unable to load educational content'
    });
  }
});

// Get specific feed item details
router.get('/feed/:itemId', async (req, res) => {
  try {
    const { itemId } = req.params;

    const feedItemDoc = await firestore.collection('educational_feed').doc(itemId).get();
    
    if (!feedItemDoc.exists) {
      return res.status(404).json({
        error: 'Feed item not found',
        item_id: itemId
      });
    }

    const feedItem = feedItemDoc.data();

    // Increment view count for analytics
    await firestore.collection('educational_feed').doc(itemId).update({
      view_count: (feedItem.view_count || 0) + 1,
      last_viewed: new Date().toISOString()
    });

    // Get related educational content
    const relatedContent = await getRelatedEducationalContent(feedItem.category, feedItem.tags, itemId);

    res.json({
      feed_item: {
        id: feedItem.id,
        title: feedItem.title,
        full_content: feedItem.full_content,
        original_claim: feedItem.original_claim,
        detailed_analysis: feedItem.detailed_analysis,
        fact_check_process: feedItem.fact_check_process,
        evidence_chain: feedItem.evidence_chain,
        visual_breakdown: feedItem.visual_breakdown,
        manipulation_techniques: feedItem.manipulation_techniques_explained,
        red_flags: feedItem.red_flags_highlighted,
        verification_steps: feedItem.verification_steps,
        source_attribution: feedItem.source_attribution,
        educational_value: feedItem.educational_value,
        published_at: feedItem.published_at
      },
      related_content: relatedContent,
      user_actions: {
        can_share: true,
        can_bookmark: true,
        can_report_error: true
      }
    });

  } catch (error) {
    logger.error('Failed to retrieve feed item', { error: error.message });
    res.status(500).json({
      error: 'Feed item retrieval failed'
    });
  }
});

// Submit engagement feedback on feed content
router.post('/feed/:itemId/engagement', async (req, res) => {
  try {
    const { itemId } = req.params;
    const { 
      engagement_type, // 'helpful', 'confusing', 'learned_something', 'share_worthy'
      rating,          // 1-5 scale
      comments = '',
      time_spent_seconds
    } = req.body;

    if (!['helpful', 'confusing', 'learned_something', 'share_worthy'].includes(engagement_type)) {
      return res.status(400).json({
        error: 'Invalid engagement type'
      });
    }

    const engagementId = require('uuid').v4();
    const engagement = {
      id: engagementId,
      feed_item_id: itemId,
      engagement_type,
      rating: parseInt(rating),
      comments,
      time_spent_seconds: parseInt(time_spent_seconds) || 0,
      user_ip: req.ip,
      user_agent: req.headers['user-agent'],
      created_at: new Date().toISOString()
    };

    // Store engagement data
    await firestore.collection('feed_engagement').doc(engagementId).set(engagement);

    // Update feed item engagement metrics
    await firestore.collection('educational_feed').doc(itemId).update({
      [`engagement_metrics.${engagement_type}`]: require('@google-cloud/firestore').FieldValue.increment(1),
      'total_engagements': require('@google-cloud/firestore').FieldValue.increment(1),
      'updated_at': new Date().toISOString()
    });

    logger.info('Feed engagement recorded', { itemId, engagementType: engagement_type });

    res.json({
      engagement_id: engagementId,
      message: 'Thank you for your feedback!',
      contribution: 'Your input helps us improve educational content'
    });

  } catch (error) {
    logger.error('Failed to record engagement', { error: error.message });
    res.status(500).json({
      error: 'Engagement recording failed'
    });
  }
});

// Get trending misinformation patterns (for educational purposes)
router.get('/trends', async (req, res) => {
  try {
    const { language = 'en', time_range = '7d' } = req.query;

    // Calculate date range
    const endDate = new Date();
    const startDate = new Date();
    const days = time_range === '30d' ? 30 : 7;
    startDate.setDate(endDate.getDate() - days);

    // Get trending patterns from recent verifications
    const trendsQuery = firestore.collection('misinformation_trends')
      .where('language', '==', language)
      .where('date_range', '==', time_range)
      .where('created_at', '>=', startDate.toISOString())
      .orderBy('trend_score', 'desc')
      .limit(5);

    const trendsSnapshot = await trendsQuery.get();
    
    const trends = trendsSnapshot.docs.map(doc => {
      const data = doc.data();
      return {
        pattern_name: data.pattern_name,
        description: data.description,
        frequency: data.frequency,
        example_claims: data.example_claims,
        detection_tips: data.detection_tips,
        related_topics: data.related_topics,
        trend_score: data.trend_score,
        educational_priority: data.educational_priority
      };
    });

    res.json({
      trending_patterns: trends,
      time_range: time_range,
      language: language,
      generated_at: new Date().toISOString(),
      disclaimer: 'Educational content for awareness and media literacy'
    });

  } catch (error) {
    logger.error('Failed to retrieve trends', { error: error.message });
    res.status(500).json({
      error: 'Trends retrieval failed'
    });
  }
});

// Helper functions
async function getTrendingTopics(language) {
  try {
    const topicsQuery = firestore.collection('trending_topics')
      .where('language', '==', language)
      .where('status', '==', 'active')
      .orderBy('trend_score', 'desc')
      .limit(5);

    const topicsSnapshot = await topicsQuery.get();
    
    return topicsSnapshot.docs.map(doc => ({
      topic: doc.data().topic,
      trend_score: doc.data().trend_score,
      category: doc.data().category
    }));
  } catch (error) {
    logger.error('Failed to get trending topics', { error: error.message });
    return [];
  }
}

async function getRelatedEducationalContent(category, tags, excludeId) {
  try {
    const relatedQuery = firestore.collection('educational_feed')
      .where('category', '==', category)
      .where('status', '==', 'published')
      .orderBy('engagement_score', 'desc')
      .limit(3);

    const relatedSnapshot = await relatedQuery.get();
    
    return relatedSnapshot.docs
      .filter(doc => doc.id !== excludeId)
      .map(doc => ({
        id: doc.data().id,
        title: doc.data().title,
        summary: doc.data().summary,
        type: doc.data().content_type
      }));
  } catch (error) {
    logger.error('Failed to get related content', { error: error.message });
    return [];
  }
}

module.exports = router;
