const { PubSub } = require('@google-cloud/pubsub');
const { Firestore } = require('@google-cloud/firestore');
const { v4: uuidv4 } = require('uuid');

const { VertexAISearch } = require('../integrations/vertexai-search');
const { FactCheckService } = require('../integrations/factcheck');
const { WebRiskService } = require('../integrations/webrisk');
const { PerspectiveService } = require('../integrations/perspective');
const { DLPService } = require('../integrations/dlp');
const { AnalysisEngine } = require('../ml/analysis-engine');

const logger = require('../utils/logger');

class AnalysisWorker {
  constructor() {
    this.firestore = new Firestore();
    this.pubsub = new PubSub();
    
    this.vertexSearch = new VertexAISearch();
    this.factCheck = new FactCheckService();
    this.webRisk = new WebRiskService();
    this.perspective = new PerspectiveService();
    this.dlp = new DLPService();
    this.analysisEngine = new AnalysisEngine();
  }

  async startListening() {
    const subscription = this.pubsub.subscription('content-analysis-sub');
    
    subscription.on('message', async (message) => {
      try {
        const data = JSON.parse(message.data.toString());
        await this.processAnalysis(data);
        message.ack();
      } catch (error) {
        logger.error('Analysis processing failed', { error: error.message });
        message.nack();
      }
    });

    logger.info('Analysis worker started listening');
  }

  async processAnalysis(data) {
    const { claim_id, text, urls = [], language, priority } = data;
    const startTime = Date.now();

    try {
      // Update claim status
      await this.updateClaimStatus(claim_id, 'processing');

      // Step 1: DLP redaction
      logger.info('Starting DLP redaction', { claim_id });
      const { redactedText, piiFound } = await this.dlp.redactPII(text, language);
      
      // Step 2: URL safety check
      const urlRisks = await Promise.all(
        urls.map(url => this.webRisk.checkUrl(url))
      );
      const safeUrls = urls.filter((_, index) => !urlRisks[index].isRisky);

      // Step 3: Content quality scoring
      const perspectiveScores = await this.perspective.analyzeText(redactedText);

      // Step 4: Evidence retrieval
      logger.info('Retrieving evidence', { claim_id });
      const evidence = await this.vertexSearch.searchEvidence(redactedText, language);

      // Step 5: Fact-check API lookup
      const factCheckMatches = await this.factCheck.searchClaims(redactedText, language);

      // Step 6: ML analysis and verdict generation
      logger.info('Generating verdict', { claim_id });
      const analysisInput = {
        text: redactedText,
        evidence,
        factCheckMatches,
        perspectiveScores,
        language
      };
      
      const verdict = await this.analysisEngine.generateVerdict(analysisInput);

      // Step 7: Store results
      await this.storeResults(claim_id, {
        evidence,
        verdict,
        piiFound,
        perspectiveScores,
        factCheckMatches,
        processingTimeMs: Date.now() - startTime
      });

      // Step 8: Update claim status
      await this.updateClaimStatus(claim_id, 'completed');

      logger.info('Analysis completed', { 
        claim_id, 
        processingTime: Date.now() - startTime,
        rating: verdict.rating 
      });

    } catch (error) {
      logger.error('Analysis failed', { claim_id, error: error.message });
      await this.updateClaimStatus(claim_id, 'failed', error.message);
      throw error;
    }
  }

  async updateClaimStatus(claimId, status, errorMessage = null) {
    const update = {
      status,
      updated_at: new Date().toISOString()
    };

    if (errorMessage) {
      update.error_message = errorMessage;
    }

    await this.firestore.collection('claims').doc(claimId).update(update);
  }

  async storeResults(claimId, results) {
    const batch = this.firestore.batch();

    // Store evidence
    for (const evidenceItem of results.evidence) {
      const evidenceId = uuidv4();
      const evidenceRef = this.firestore.collection('evidence').doc(evidenceId);
      batch.set(evidenceRef, {
        id: evidenceId,
        claim_id: claimId,
        ...evidenceItem,
        created_at: new Date().toISOString()
      });
    }

    // Store verdict
    const verdictId = uuidv4();
    const verdictRef = this.firestore.collection('verdicts').doc(verdictId);
    batch.set(verdictRef, {
      id: verdictId,
      claim_id: claimId,
      ...results.verdict,
      detection_scores: results.perspectiveScores,
      fact_check_matches: results.factCheckMatches,
      processing_time_ms: results.processingTimeMs,
      created_at: new Date().toISOString()
    });

    await batch.commit();
  }
}

// Start worker if running directly
if (require.main === module) {
  const worker = new AnalysisWorker();
  worker.startListening().catch(error => {
    logger.error('Worker startup failed', { error: error.message });
    process.exit(1);
  });
}

module.exports = AnalysisWorker;
