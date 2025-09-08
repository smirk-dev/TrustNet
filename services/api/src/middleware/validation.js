const Joi = require('joi');

const analysisRequestSchema = Joi.object({
  text: Joi.string().min(10).max(10000).required(),
  urls: Joi.array().items(Joi.string().uri()).max(5).optional(),
  images: Joi.array().items(Joi.string().uri()).max(3).optional(),
  language: Joi.string().valid(
    'hi', 'bn', 'te', 'mr', 'ta', 'kn', 'ml', 'gu', 'or', 'pa', 'ur', 'en'
  ).optional(),
  source_type: Joi.string().valid(
    'social_media', 'news', 'messaging', 'email', 'web'
  ).optional(),
  user_segment: Joi.string().valid(
    'journalist', 'educator', 'citizen', 'fact_checker'
  ).optional(),
  priority: Joi.string().valid('low', 'normal', 'high').optional()
});

const feedbackSchema = Joi.object({
  verdict_id: Joi.string().uuid().required(),
  user_rating: Joi.string().valid('accurate', 'inaccurate', 'partially_accurate').required(),
  feedback_type: Joi.string().valid(
    'rating_disagreement', 'missing_evidence', 'poor_explanation', 'factual_error'
  ).required(),
  comments: Joi.string().max(1000).optional(),
  user_expertise: Joi.string().valid('expert', 'knowledgeable', 'general_public').optional()
});

const validateAnalysisRequest = (req, res, next) => {
  const { error, value } = analysisRequestSchema.validate(req.body);
  
  if (error) {
    return res.status(400).json({
      error: 'Invalid request format',
      details: error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }))
    });
  }
  
  req.body = value;
  next();
};

const validateFeedback = (req, res, next) => {
  const { error, value } = feedbackSchema.validate(req.body);
  
  if (error) {
    return res.status(400).json({
      error: 'Invalid feedback format',
      details: error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }))
    });
  }
  
  req.body = value;
  next();
};

module.exports = {
  validateAnalysisRequest,
  validateFeedback
};
