const { DlpServiceClient } = require('@google-cloud/dlp');

class DLPService {
  constructor() {
    this.client = new DlpServiceClient();
    this.projectId = process.env.GOOGLE_CLOUD_PROJECT_ID;
  }

  async redactPII(text, language = 'en') {
    try {
      // Configure info types for Indian context
      const infoTypes = [
        { name: 'PERSON_NAME' },
        { name: 'PHONE_NUMBER' },
        { name: 'EMAIL_ADDRESS' },
        { name: 'CREDIT_CARD_NUMBER' },
        { name: 'INDIA_PAN' },
        { name: 'INDIA_AADHAAR' }
      ];

      const inspectConfig = {
        infoTypes: infoTypes,
        minLikelihood: 'LIKELY',
        includeQuote: true,
        limits: {
          maxFindingsPerRequest: 100
        }
      };

      const deidentifyConfig = {
        infoTypeTransformations: {
          transformations: [
            {
              primitiveTransformation: {
                replaceWithInfoTypeConfig: {
                  // Replace with [REDACTED-TYPE] format
                }
              }
            }
          ]
        }
      };

      const request = {
        parent: `projects/${this.projectId}`,
        item: {
          value: text
        },
        inspectConfig,
        deidentifyConfig
      };

      const [response] = await this.client.deidentifyContent(request);

      return {
        redactedText: response.item.value,
        piiFound: response.overview?.transformationSummaries?.length > 0,
        findings: response.overview?.transformationSummaries || []
      };

    } catch (error) {
      console.error('DLP redaction failed:', error);
      // Return original text if DLP fails
      return {
        redactedText: text,
        piiFound: false,
        findings: [],
        error: error.message
      };
    }
  }

  async inspectOnly(text, language = 'en') {
    try {
      const infoTypes = [
        { name: 'PERSON_NAME' },
        { name: 'PHONE_NUMBER' },
        { name: 'EMAIL_ADDRESS' },
        { name: 'INDIA_PAN' },
        { name: 'INDIA_AADHAAR' }
      ];

      const inspectConfig = {
        infoTypes: infoTypes,
        minLikelihood: 'POSSIBLE',
        includeQuote: true
      };

      const request = {
        parent: `projects/${this.projectId}`,
        item: {
          value: text
        },
        inspectConfig
      };

      const [response] = await this.client.inspectContent(request);
      
      return {
        findings: response.result?.findings || [],
        hasPII: (response.result?.findings || []).length > 0
      };

    } catch (error) {
      console.error('DLP inspection failed:', error);
      return {
        findings: [],
        hasPII: false,
        error: error.message
      };
    }
  }
}

module.exports = { DLPService };
