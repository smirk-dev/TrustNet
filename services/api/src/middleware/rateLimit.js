const rateLimit = require('express-rate-limit');
const { Firestore } = require('@google-cloud/firestore');

const firestore = new Firestore();

// Basic rate limiting
const rateLimitMiddleware = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests',
    message: 'Rate limit exceeded. Please try again later.',
    retry_after: '15 minutes'
  },
  standardHeaders: true,
  legacyHeaders: false,
  // Custom key generator for user-based rate limiting
  keyGenerator: (req) => {
    return req.ip || 'anonymous';
  },
  // Skip successful requests in rate limit count
  skipSuccessfulRequests: false,
  // Skip failed requests
  skipFailedRequests: true
});

// Advanced rate limiting with user tiers
const createTieredRateLimit = (tier) => {
  const limits = {
    free: { windowMs: 60 * 60 * 1000, max: 50 }, // 50/hour
    basic: { windowMs: 60 * 60 * 1000, max: 500 }, // 500/hour  
    premium: { windowMs: 60 * 60 * 1000, max: 2000 } // 2000/hour
  };

  return rateLimit({
    ...limits[tier],
    message: {
      error: 'Rate limit exceeded',
      tier: tier,
      message: `${tier} tier limit reached. Upgrade for higher limits.`
    }
  });
};

module.exports = {
  rateLimitMiddleware,
  createTieredRateLimit
};
