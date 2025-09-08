const { google } = require('googleapis');

class PerspectiveService {
  constructor() {
    this.apiKey = process.env.PERSPECTIVE_API_KEY;
    this.client = google.commentanalyzer('v1alpha1');
    
    // Attributes to analyze
    this.attributes = [
      'TOXICITY',
      'SEVERE_TOXICITY', 
      'IDENTITY_ATTACK',
      'INSULT',
      'PROFANITY',
      'THREAT'
    ];
  }

  async analyzeText(text, language = 'en') {
    try {
      const promises = this.attributes.map(attribute => 
        this.analyzeAttribute(text, attribute, language)
      );

      const results = await Promise.all(promises);
      
      // Combine results into single score object
      const scores = {};
      results.forEach((result, index) => {
        const attribute = this.attributes[index];
        scores[attribute.toLowerCase()] = result.score;
      });

      // Calculate overall credibility signal
      scores.credibility_signal = this.calculateCredibilitySignal(scores);

      return scores;

    } catch (error) {
      console.error('Perspective API error:', error);
      // Return neutral scores if API fails
      return this.getNeutralScores();
    }
  }

  async analyzeAttribute(text, attribute, language) {
    try {
      const request = {
        key: this.apiKey,
        resource: {
          requestedAttributes: {
            [attribute]: {}
          },
          comment: {
            text: text
          },
          languages: [language],
          doNotStore: true
        }
      };

      const response = await this.client.comments.analyze(request);
      const score = response.data.attributeScores[attribute].summaryScore.value;
      
      return {
        attribute: attribute,
        score: score,
        language: language
      };

    } catch (error) {
      console.error(`Perspective ${attribute} analysis failed:`, error);
      return {
        attribute: attribute,
        score: 0.5, // Neutral score
        error: error.message
      };
    }
  }

  calculateCredibilitySignal(scores) {
    // Higher toxicity/spam = lower credibility
    const toxicityPenalty = scores.toxicity * 0.4;
    const severeToxicityPenalty = scores.severe_toxicity * 0.6;
    const identityAttackPenalty = scores.identity_attack * 0.3;
    const insultPenalty = scores.insult * 0.2;
    const threatPenalty = scores.threat * 0.8;
    
    const totalPenalty = toxicityPenalty + severeToxicityPenalty + 
                        identityAttackPenalty + insultPenalty + threatPenalty;
    
    // Credibility ranges from 0 (toxic) to 1 (clean)
    return Math.max(0, 1 - totalPenalty);
  }

  getNeutralScores() {
    const scores = {};
    this.attributes.forEach(attr => {
      scores[attr.toLowerCase()] = 0.5;
    });
    scores.credibility_signal = 0.5;
    return scores;
  }
}

module.exports = { PerspectiveService };
