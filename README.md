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

- **Multi-language Support**: Hindi, Bengali, Telugu, Marathi, Tamil, and more
- **Real-time Analysis**: <3 second response times for content verification
- **Evidence Retrieval**: Grounded explanations with cited sources
- **Educational Tips**: Media literacy guidance for users
- **Mobile-First**: PWA optimized for low-bandwidth networks

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