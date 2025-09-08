const { WebRiskServiceClient } = require('@google-cloud/web-risk');

class WebRiskService {
  constructor() {
    this.client = new WebRiskServiceClient();
    this.threatTypes = [
      'MALWARE',
      'SOCIAL_ENGINEERING', 
      'UNWANTED_SOFTWARE',
      'POTENTIALLY_HARMFUL_APPLICATION'
    ];
  }

  async checkUrl(url) {
    try {
      const request = {
        uri: url,
        threatTypes: this.threatTypes
      };

      const [response] = await this.client.searchUris(request);
      
      const isRisky = response.threat && response.threat.threatTypes.length > 0;
      
      return {
        url: url,
        isRisky: isRisky,
        threatTypes: response.threat?.threatTypes || [],
        expireTime: response.threat?.expireTime,
        checked_at: new Date().toISOString()
      };

    } catch (error) {
      console.error('Web Risk API error:', error);
      // If API fails, allow URL but log the error
      return {
        url: url,
        isRisky: false,
        threatTypes: [],
        error: error.message,
        checked_at: new Date().toISOString()
      };
    }
  }

  async checkUrls(urls) {
    const promises = urls.map(url => this.checkUrl(url));
    return Promise.all(promises);
  }

  async submitUri(uri, threatType) {
    try {
      const request = {
        parent: `projects/${process.env.GOOGLE_CLOUD_PROJECT_ID}`,
        submission: {
          uri: uri,
          threatTypes: [threatType]
        }
      };

      const [response] = await this.client.createSubmission(request);
      return response;

    } catch (error) {
      console.error('Failed to submit URI to Web Risk:', error);
      throw error;
    }
  }
}

module.exports = { WebRiskService };
