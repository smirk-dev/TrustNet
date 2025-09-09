const { VertexAI } = require('@google-cloud/aiplatform');
const { v4: uuidv4 } = require('uuid');

class ManipulationDetectionEngine {
  constructor() {
    this.vertexAI = new VertexAI({
      project: process.env.GOOGLE_CLOUD_PROJECT_ID,
      location: 'us-central1'
    });
  }

  // Core Detection Principle: Manipulates Emotion
  async detectEmotionalManipulation(text, language = 'en') {
    try {
      const emotionalTriggers = {
        'hi': ['तुरंत', 'खतरा', 'गुप्त', 'चमत्कार', 'डरावना'],
        'en': ['urgent', 'secret', 'shocking', 'dangerous', 'miracle', 'breaking', 'exclusive']
      };

      const triggers = emotionalTriggers[language] || emotionalTriggers['en'];
      const foundTriggers = triggers.filter(trigger => 
        text.toLowerCase().includes(trigger.toLowerCase())
      );

      // Analyze emotional language patterns
      const emotionalPrompt = `
        Analyze this text for emotional manipulation tactics:
        Text: "${text}"
        
        Rate on scale 0-1:
        1. Urgency pressure (time-sensitive language)
        2. Fear appeals (danger, threat language)  
        3. Exclusive claims (secret knowledge)
        4. Miraculous benefits (too good to be true)
        5. Authority pressure (must believe this)
        
        Return JSON format with scores for each category.
      `;

      const model = this.vertexAI.preview.getGenerativeModel({
        model: 'gemini-pro',
        generationConfig: { 
          temperature: 0.1,
          candidateCount: 1,
          maxOutputTokens: 500
        }
      });

      const response = await model.generateContent(emotionalPrompt);
      const scores = JSON.parse(response.response.candidates[0].content.parts[0].text);

      return {
        manipulation_score: Math.max(...Object.values(scores)),
        emotional_triggers: foundTriggers,
        manipulation_tactics: scores,
        confidence: foundTriggers.length > 0 ? 0.8 : 0.4
      };

    } catch (error) {
      console.error('Emotional manipulation detection failed:', error);
      return {
        manipulation_score: 0.5,
        emotional_triggers: [],
        manipulation_tactics: {},
        confidence: 0.2,
        error: error.message
      };
    }
  }

  // Core Detection Principle: Unrealistic Incentives
  async detectUnrealisticIncentives(text, urls = []) {
    try {
      const incentivePatterns = [
        /earn (\$|₹|rs\.?)\s*\d+.*?(daily|hour|minute)/i,
        /(free|मुफ्त).*?(money|पैसा|cash|loan)/i,
        /(guaranteed|गारंटी).*?(profit|win|success)/i,
        /(work from home|घर से काम).*?(\$|₹)\d+/i,
        /(lose \d+.*?(kg|pounds)|वजन.*?\d+.*?kg)/i
      ];

      const foundPatterns = incentivePatterns.filter(pattern => pattern.test(text));
      
      // Check URLs for suspicious domains
      const suspiciousUrlPatterns = [
        /bit\.ly|tinyurl|t\.co/i,  // URL shorteners hiding destination
        /\d+\.\w+\.(tk|ml|ga|cf)/i, // Free domains often used for scams
        /earn.*?money.*?\.(com|net|org)/i
      ];

      const suspiciousUrls = urls.filter(url => 
        suspiciousUrlPatterns.some(pattern => pattern.test(url))
      );

      const incentiveScore = foundPatterns.length > 0 ? 0.8 : 0.1;
      const urlScore = suspiciousUrls.length > 0 ? 0.7 : 0.0;

      return {
        unrealistic_incentive_score: Math.max(incentiveScore, urlScore),
        found_patterns: foundPatterns.map(p => p.toString()),
        suspicious_urls: suspiciousUrls,
        risk_indicators: {
          monetary_promises: incentivePatterns[0].test(text),
          free_money_offers: incentivePatterns[1].test(text),
          guaranteed_returns: incentivePatterns[2].test(text),
          work_from_home_scam: incentivePatterns[3].test(text),
          miracle_weight_loss: incentivePatterns[4].test(text)
        },
        confidence: foundPatterns.length > 0 || suspiciousUrls.length > 0 ? 0.8 : 0.3
      };

    } catch (error) {
      console.error('Incentive detection failed:', error);
      return {
        unrealistic_incentive_score: 0.3,
        found_patterns: [],
        suspicious_urls: [],
        risk_indicators: {},
        confidence: 0.2
      };
    }
  }

  // Core Detection Principle: Technical Deception
  async detectTechnicalDeception(text, urls = []) {
    try {
      const deceptionIndicators = {
        link_masking: [],
        impersonation: [],
        technical_jargon: [],
        fake_credentials: []
      };

      // Check for link masking in text
      const linkMaskingPatterns = [
        /click here|यहाँ क्लिक करें/i,
        /bit\.ly|tinyurl|short\.link/i,
        /download now|अभी डाउनलोड करें/i
      ];

      deceptionIndicators.link_masking = linkMaskingPatterns.filter(pattern => pattern.test(text));

      // Check for impersonation attempts
      const impersonationPatterns = [
        /(official|आधिकारिक).*?(government|सरकार|ministry)/i,
        /(WhatsApp|facebook).*?(admin|administrator)/i,
        /(bank|बैंक).*?(notice|नोटिस|alert)/i,
        /(COVID|corona).*?(ministry|health|WHO)/i
      ];

      deceptionIndicators.impersonation = impersonationPatterns.filter(pattern => pattern.test(text));

      // Check URLs for technical deception
      const urlDeceptionScore = this.analyzeUrlDeception(urls);

      const totalDeceptionScore = [
        deceptionIndicators.link_masking.length * 0.3,
        deceptionIndicators.impersonation.length * 0.4,
        urlDeceptionScore
      ].reduce((sum, score) => sum + score, 0);

      return {
        technical_deception_score: Math.min(totalDeceptionScore, 1.0),
        deception_indicators: deceptionIndicators,
        url_analysis: this.analyzeUrlStructure(urls),
        confidence: totalDeceptionScore > 0.3 ? 0.8 : 0.4
      };

    } catch (error) {
      console.error('Technical deception detection failed:', error);
      return {
        technical_deception_score: 0.4,
        deception_indicators: {},
        confidence: 0.2
      };
    }
  }

  // Core Detection Principle: Synthetic Media Detection
  async detectSyntheticMedia(text, imageUrls = []) {
    try {
      // Text-based synthetic content detection
      const aiGeneratedPatterns = [
        /as an ai|i am an artificial/i,
        /generated by ai|ai generated/i,
        /this is a computer-generated/i
      ];

      const syntheticTextIndicators = aiGeneratedPatterns.filter(pattern => pattern.test(text));

      // Analyze text for AI generation characteristics
      const aiTextPrompt = `
        Analyze if this text might be AI-generated:
        "${text}"
        
        Look for:
        1. Repetitive patterns typical of AI
        2. Unusual phrasing or structure
        3. Generic or template-like language
        4. Inconsistent tone or style
        
        Return probability (0-1) that this is AI-generated.
      `;

      let aiGenerationScore = 0.2; // Default low score
      
      try {
        const model = this.vertexAI.preview.getGenerativeModel({
          model: 'gemini-pro',
          generationConfig: { temperature: 0.1 }
        });

        const response = await model.generateContent(aiTextPrompt);
        const result = response.response.candidates[0].content.parts[0].text;
        aiGenerationScore = parseFloat(result.match(/(\d*\.?\d+)/)?.[1] || '0.2');
      } catch (modelError) {
        console.warn('AI text analysis failed, using heuristics');
      }

      return {
        synthetic_media_score: Math.max(aiGenerationScore, syntheticTextIndicators.length * 0.3),
        ai_text_probability: aiGenerationScore,
        synthetic_indicators: syntheticTextIndicators,
        image_analysis_needed: imageUrls.length > 0,
        confidence: syntheticTextIndicators.length > 0 ? 0.7 : 0.4
      };

    } catch (error) {
      console.error('Synthetic media detection failed:', error);
      return {
        synthetic_media_score: 0.3,
        ai_text_probability: 0.3,
        synthetic_indicators: [],
        confidence: 0.2
      };
    }
  }

  // Comprehensive manipulation analysis combining all principles
  async analyzeManipulationPattern(text, urls = [], imageUrls = [], language = 'en') {
    try {
      const [
        emotionalAnalysis,
        incentiveAnalysis, 
        technicalAnalysis,
        syntheticAnalysis
      ] = await Promise.all([
        this.detectEmotionalManipulation(text, language),
        this.detectUnrealisticIncentives(text, urls),
        this.detectTechnicalDeception(text, urls),
        this.detectSyntheticMedia(text, imageUrls)
      ]);

      // Calculate overall manipulation score
      const overallScore = (
        emotionalAnalysis.manipulation_score * 0.3 +
        incentiveAnalysis.unrealistic_incentive_score * 0.25 +
        technicalAnalysis.technical_deception_score * 0.25 +
        syntheticAnalysis.synthetic_media_score * 0.2
      );

      // Determine confidence level
      const avgConfidence = [
        emotionalAnalysis.confidence,
        incentiveAnalysis.confidence,
        technicalAnalysis.confidence,
        syntheticAnalysis.confidence
      ].reduce((sum, conf) => sum + conf, 0) / 4;

      // Generate High Manipulation Alert if multiple indicators present
      const highManipulationAlert = this.generateHighManipulationAlert(
        emotionalAnalysis,
        incentiveAnalysis,
        technicalAnalysis,
        syntheticAnalysis
      );

      return {
        overall_manipulation_score: overallScore,
        confidence_score: avgConfidence,
        detailed_analysis: {
          emotional_manipulation: emotionalAnalysis,
          unrealistic_incentives: incentiveAnalysis,
          technical_deception: technicalAnalysis,
          synthetic_media: syntheticAnalysis
        },
        high_manipulation_alert: highManipulationAlert,
        risk_level: this.determineRiskLevel(overallScore, avgConfidence),
        educational_recommendations: this.generateEducationalTips(
          emotionalAnalysis,
          incentiveAnalysis,
          technicalAnalysis,
          syntheticAnalysis
        )
      };

    } catch (error) {
      console.error('Comprehensive manipulation analysis failed:', error);
      return {
        overall_manipulation_score: 0.5,
        confidence_score: 0.2,
        error: error.message
      };
    }
  }

  // Helper Methods
  analyzeUrlDeception(urls) {
    if (!urls.length) return 0;

    let deceptionScore = 0;
    for (const url of urls) {
      // Check for URL shorteners
      if (/bit\.ly|tinyurl|t\.co|short\.link/i.test(url)) {
        deceptionScore += 0.3;
      }
      
      // Check for suspicious TLDs
      if (/\.(tk|ml|ga|cf|click|download)$/i.test(url)) {
        deceptionScore += 0.4;
      }
      
      // Check for typosquatting
      const suspiciousDomains = ['google', 'facebook', 'whatsapp', 'amazon', 'microsoft'];
      for (const domain of suspiciousDomains) {
        if (url.includes(domain) && !url.includes(`.${domain}.com`)) {
          deceptionScore += 0.5;
        }
      }
    }

    return Math.min(deceptionScore, 1.0);
  }

  analyzeUrlStructure(urls) {
    return urls.map(url => {
      try {
        const urlObj = new URL(url);
        return {
          url: url,
          domain: urlObj.hostname,
          suspicious_tld: /\.(tk|ml|ga|cf)$/i.test(urlObj.hostname),
          url_shortener: /bit\.ly|tinyurl|t\.co/i.test(urlObj.hostname),
          excessive_subdomains: urlObj.hostname.split('.').length > 4
        };
      } catch (error) {
        return { url, error: 'Invalid URL format' };
      }
    });
  }

  generateHighManipulationAlert(emotional, incentive, technical, synthetic) {
    const triggers = [];
    
    if (emotional.manipulation_score > 0.6 && synthetic.synthetic_media_score > 0.5) {
      triggers.push({
        type: 'emotional_with_synthetic',
        severity: 'high',
        message: 'Content combines emotional manipulation with potentially AI-generated elements'
      });
    }

    if (incentive.unrealistic_incentive_score > 0.7 && technical.technical_deception_score > 0.5) {
      triggers.push({
        type: 'deceptive_incentive',
        severity: 'high', 
        message: 'Suspicious money-making claims with hidden or deceptive links'
      });
    }

    return {
      alerts: triggers,
      should_alert: triggers.length > 0,
      combined_risk_score: triggers.length > 0 ? 0.8 : 0.3
    };
  }

  determineRiskLevel(overallScore, confidence) {
    if (overallScore >= 0.7 && confidence >= 0.6) return 'high';
    if (overallScore >= 0.5 && confidence >= 0.5) return 'medium';
    if (overallScore >= 0.3) return 'low';
    return 'minimal';
  }

  generateEducationalTips(emotional, incentive, technical, synthetic) {
    const tips = [];

    if (emotional.manipulation_score > 0.5) {
      tips.push({
        category: 'emotional_awareness',
        tip: 'Be cautious of urgent language designed to bypass critical thinking',
        principle: 'Misinformation often uses emotional pressure to prevent verification'
      });
    }

    if (incentive.unrealistic_incentive_score > 0.5) {
      tips.push({
        category: 'incentive_skepticism', 
        tip: 'Question offers that seem too good to be true - they usually are',
        principle: 'Legitimate opportunities rarely require urgent action or secrecy'
      });
    }

    if (technical.technical_deception_score > 0.5) {
      tips.push({
        category: 'technical_verification',
        tip: 'Verify official communications directly through official channels',
        principle: 'Hover over links to see actual destinations before clicking'
      });
    }

    if (synthetic.synthetic_media_score > 0.5) {
      tips.push({
        category: 'media_literacy',
        tip: 'Be aware that AI can now generate realistic text and images',
        principle: 'Cross-check AI-generated looking content with multiple sources'
      });
    }

    return tips;
  }
}

module.exports = { ManipulationDetectionEngine };
