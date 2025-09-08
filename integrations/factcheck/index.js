const { google } = require('googleapis');

class FactCheckService {
  constructor() {
    this.apiKey = process.env.FACT_CHECK_API_KEY;
    this.client = google.factchecktools('v1alpha1');
  }

  async searchClaims(query, language = 'en') {
    try {
      const request = {
        key: this.apiKey,
        query: query,
        languageCode: language,
        maxAgeDays: 365 // Only recent fact-checks
      };

      const response = await this.client.claims.search(request);
      
      if (!response.data.claims) {
        return [];
      }

      return response.data.claims.map(claim => ({
        text: claim.text,
        claimant: claim.claimant,
        claimDate: claim.claimDate,
        claimReview: claim.claimReview?.map(review => ({
          publisher: review.publisher?.name,
          url: review.url,
          title: review.title,
          reviewDate: review.reviewDate,
          textualRating: review.textualRating,
          languageCode: review.languageCode
        })) || []
      }));

    } catch (error) {
      console.error('Fact Check API error:', error);
      return [];
    }
  }

  async searchImages(imageUrl, language = 'en') {
    try {
      const request = {
        key: this.apiKey,
        imageUri: imageUrl,
        languageCode: language
      };

      const response = await this.client.claims.imageSearch(request);
      
      if (!response.data.claims) {
        return [];
      }

      return response.data.claims.map(claim => ({
        text: claim.text,
        claimant: claim.claimant,
        claimDate: claim.claimDate,
        imageUrl: imageUrl,
        claimReview: claim.claimReview?.map(review => ({
          publisher: review.publisher?.name,
          url: review.url,
          title: review.title,
          reviewDate: review.reviewDate,
          textualRating: review.textualRating,
          languageCode: review.languageCode
        })) || []
      }));

    } catch (error) {
      console.error('Fact Check Image API error:', error);
      return [];
    }
  }

  async searchByUrl(url, language = 'en') {
    try {
      // Extract main content from URL for text-based search
      // This would typically involve web scraping or content extraction
      const request = {
        key: this.apiKey,
        query: url,
        languageCode: language,
        maxAgeDays: 365
      };

      const response = await this.client.claims.search(request);
      
      if (!response.data.claims) {
        return [];
      }

      return response.data.claims.map(claim => ({
        text: claim.text,
        claimant: claim.claimant,
        claimDate: claim.claimDate,
        sourceUrl: url,
        claimReview: claim.claimReview?.map(review => ({
          publisher: review.publisher?.name,
          url: review.url,
          title: review.title,
          reviewDate: review.reviewDate,
          textualRating: review.textualRating,
          languageCode: review.languageCode
        })) || []
      }));

    } catch (error) {
      console.error('Fact Check URL search error:', error);
      return [];
    }
  }

  // Convert fact-check ratings to standardized format
  normalizeRating(textualRating) {
    const rating = textualRating?.toLowerCase() || '';
    
    if (rating.includes('true') || rating.includes('correct') || rating.includes('accurate')) {
      return 'True';
    } else if (rating.includes('false') || rating.includes('incorrect') || rating.includes('inaccurate')) {
      return 'False';
    } else if (rating.includes('mixed') || rating.includes('partly') || rating.includes('partial')) {
      return 'Mixture';
    } else if (rating.includes('unproven') || rating.includes('unverified')) {
      return 'Unproven';
    } else {
      return 'Insufficient_Evidence';
    }
  }

  // Calculate confidence based on source quality and recency
  calculateConfidence(claimReviews) {
    if (!claimReviews || claimReviews.length === 0) {
      return 0.1;
    }

    let totalScore = 0;
    let count = 0;

    for (const review of claimReviews) {
      let score = 0.5; // Base score
      
      // Boost for known reliable fact-checkers
      const reliableSources = ['snopes', 'politifact', 'factcheck.org', 'reuters', 'ap'];
      if (reliableSources.some(source => review.url?.includes(source))) {
        score += 0.3;
      }

      // Recency bonus (more recent = higher confidence)
      if (review.reviewDate) {
        const reviewAge = Date.now() - new Date(review.reviewDate).getTime();
        const daysAge = reviewAge / (1000 * 60 * 60 * 24);
        if (daysAge < 30) score += 0.2;
        else if (daysAge < 180) score += 0.1;
      }

      totalScore += Math.min(score, 1.0);
      count++;
    }

    return count > 0 ? totalScore / count : 0.1;
  }
}

module.exports = { FactCheckService };
