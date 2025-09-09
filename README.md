# TrustNet

AI-powered misinformation detection system for India using Google Cloud services.

## Quick Start

```bash
# Clone repository
git clone https://github.com/smirk-dev/TrustNet.git
cd TrustNet

# Set up Google Cloud project
gcloud config set project trustnet-dev
gcloud auth application-default login

# Deploy infrastructure
cd infra/terraform
terraform init && terraform apply

# Deploy services
cd ../../scripts/deploy
./deploy-services.sh

# Run locally
cd ../../services/api
npm install && npm run dev
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design, data models, and deployment instructions.

## Features

### 🔍 **Automated Verification Engine** (MVP Priority #1)
- **Instant Credibility Scoring**: Get immediate assessment of content trustworthiness
- **Source Analysis**: Automated checking of URLs and domain reputation
- **Neutral AI Summaries**: Unbiased summaries of claims with alternative perspectives
- **High Manipulation Alerts**: Combined detection for emotional triggers + synthetic media

### 🏠 **Quarantine Room** (MVP Priority #2)  
- **Human-AI Collaboration**: When AI is uncertain, users provide the final judgment
- **Educational Context**: Learn why content is suspicious through interactive analysis
- **User Empowerment**: Build critical thinking skills by reviewing "grey area" content
- **Feedback Loop**: User verdicts improve AI detection for everyone

### 📚 **Proactive Homepage Feed** (MVP Priority #3)
- **Real-World Examples**: Curated verified and debunked information for continuous learning
- **Pattern Recognition**: Learn to identify manipulation techniques through examples
- **Trending Analysis**: Stay aware of current misinformation patterns in your language
- **Engagement Tracking**: Educational content that adapts based on user interaction

### 🛡️ **Advanced Detection Principles**
- **Emotional Manipulation**: Identifies urgency, fear appeals, and pressure tactics
- **Unrealistic Incentives**: Flags too-good-to-be-true offers and get-rich-quick schemes  
- **Technical Deception**: Detects link masking, impersonation, and fake credentials
- **Synthetic Media**: AI-generated text and image detection with confidence scoring
- **Visual Analysis**: Highlights suspicious areas in images and data visualizations

### 🌐 **No-Login MVP Experience**
- **Friction-Free Access**: Start verifying content immediately without registration
- **Privacy-First**: Minimal data collection with optional engagement tracking
- **Mobile Optimized**: Works seamlessly on low-end Android devices with limited bandwidth

## API Usage

```bash
# Analyze text content
curl -X POST https://api.trustnet.dev/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "वैक्सीन में माइक्रोचिप्स होती हैं", "language": "hi"}'

# Get analysis results
curl https://api.trustnet.dev/v1/claims/{claim-id}
```

## Development

```bash
# Install dependencies
npm install

# Run tests
npm test

# Start development server
npm run dev

# Deploy to staging
npm run deploy:staging
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.