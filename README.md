# ðŸ›¡ï¸ TrustNet - AI-Powered Misinformation Detection Platform

A comprehensive fullstack application that empowers users to identify misinformation and build digital immunity through AI-powered content analysis, educational insights, and real-time verification.

![TrustNet](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![React](https://img.shields.io/badge/Frontend-React%2018.3.1-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![TypeScript](https://img.shields.io/badge/Language-TypeScript-blue)

## ðŸš€ Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Modern web browser**

### 1. Clone & Setup
```bash
git clone https://github.com/smirk-dev/TrustNet.git
cd TrustNet
```

### 2. Start Backend Server
```bash
cd services/api-python
pip install fastapi uvicorn pydantic
python basic_server.py
```
**Backend will run on:** http://localhost:8000

### 3. Start Frontend Server
```bash
cd mind-guard-toolkit-main
npm install
npm run dev
```
**Frontend will run on:** http://localhost:8080

### 4. Open Application
Navigate to **http://localhost:8080** in your browser and start analyzing content!

## ðŸ—ï¸ Architecture

**Fullstack Application Structure:**

```text
TrustNet/
â”œâ”€â”€ mind-guard-toolkit-main/          # React Frontend
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ components/               # UI Components
â”‚   â”‚   â”œâ”€â”€ hooks/                    # React Hooks & API Integration
â”‚   â”‚   â”œâ”€â”€ lib/                     # API Client & Configuration
â”‚   â”‚   â””â”€â”€ pages/                   # Application Pages
â”‚   â””â”€â”€ package.json                 # Frontend Dependencies
â”œâ”€â”€ services/
â”‚   â”œâ”€â”€ api-python/                  # FastAPI Backend
â”‚   â”‚   â”œâ”€â”€ app/                     # Application Logic
â”‚   â”‚   â”œâ”€â”€ basic_server.py          # Simplified API Server
â”‚   â”‚   â””â”€â”€ requirements.txt         # Backend Dependencies
â”‚   â””â”€â”€ workers/                     # Background Processing
â”œâ”€â”€ infra/                           # Infrastructure as Code
â””â”€â”€ docs/                           # Documentation
```

**Technology Stack:**

- **Frontend**: React 18.3.1, TypeScript, Vite, TanStack Query, shadcn/ui
- **Backend**: Python FastAPI, Pydantic, Uvicorn
- **Styling**: Tailwind CSS with animations and dark mode
- **State Management**: TanStack Query for server state
- **Build Tool**: Vite for fast development and optimized builds

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design and deployment instructions.

## âœ¨ Features

### ðŸ” **Real-Time Content Analysis**

- **Instant Trust Scoring**: Get immediate credibility assessment (0-100% scale)
- **Manipulation Detection**: Identifies emotional appeals, urgency tactics, and bias
- **Educational Insights**: Learn why content is flagged with detailed explanations
- **Source Verification**: Automatic checking of URLs and domain reputation

### ðŸŽ¨ **Modern User Interface**

- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Dark/Light Mode**: Automatic theme switching with user preference
- **Real-time Feedback**: Live analysis with progress indicators
- **File Upload Support**: Analyze documents, images, and text files

### ðŸ§  **Digital Immunity Building**

- **Pattern Recognition**: Learn to identify manipulation techniques
- **Educational Tips**: Context-aware guidance for each analysis
- **Progressive Learning**: Build critical thinking skills over time
- **Safe Testing Environment**: Practice with various content types

### ðŸ”„ **Seamless Integration**

- **RESTful API**: Easy integration with external applications
- **Real-time Processing**: Immediate results with streaming updates
- **Cross-platform**: Works on all modern browsers and devices
- **No Registration Required**: Start analyzing content immediately

## ðŸ”§ API Documentation

### Endpoints

#### Health Check

```bash
GET http://localhost:8000/health
# Response: {"status": "healthy"}
```

#### Content Analysis

```bash
POST http://localhost:8000/v1/analysis
Content-Type: application/json

{
  "content": "Your content to analyze here",
  "content_type": "text",
  "user_id": "anonymous"
}
```

#### Response Format

```json
{
  "analysis_id": "test_1234567890",
  "trust_score": {
    "overall_score": 0.75,
    "credibility": 0.78,
    "bias_score": 0.5,
    "emotional_manipulation": 0.25,
    "source_reliability": 0.75
  },
  "analysis_summary": "Content analysis results...",
  "manipulation_techniques": [],
  "educational_content": "Educational insights...",
  "metadata": {
    "word_count": 10,
    "sources": ["Source 1"]
  },
  "timestamp": 1234567890.123
}
```

### Frontend API Integration

The frontend uses TanStack Query for efficient API state management:

```typescript
import { useAnalysis } from '@/hooks/useApi';

const { analyzeContent, isAnalyzing, data, error } = useAnalysis();

// Analyze content
analyzeContent({
  content: "Text to analyze",
  content_type: "text",
  user_id: "user123"
});
```

## ðŸ’» Development

### Frontend Development

```bash
cd mind-guard-toolkit-main

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

### Backend Development

```bash
cd services/api-python

# Install dependencies
pip install fastapi uvicorn pydantic pydantic-settings

# Start development server
python basic_server.py

# Run with auto-reload
python -m uvicorn basic_server:app --reload --port 8000
```

### Environment Configuration

Create environment files for different environments:

#### Frontend (.env.development)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_NODE_ENV=development
VITE_ENABLE_DEBUG=true
```

#### Backend Configuration

The backend uses pydantic-settings for configuration management. Key settings include CORS origins, API endpoints, and feature flags.

### Testing

```bash
# Frontend tests
cd mind-guard-toolkit-main
npm test

# Backend tests
cd services/api-python
python -m pytest

# API testing
curl http://localhost:8000/health
```

## ðŸš€ Deployment

### Production Build

```bash
# Build frontend
npm run build

# Serve static files or deploy to CDN
```

### Environment Variables

- `VITE_API_BASE_URL`: Backend API URL
- `VITE_ENABLE_ANALYTICS`: Enable/disable analytics
- `VITE_ENABLE_DEBUG`: Debug mode toggle

## ðŸ¤ Contributing

We welcome contributions to TrustNet! Here's how you can help:

### Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/TrustNet.git
   cd TrustNet
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Set up development environment**
   ```bash
   # Install frontend dependencies
   cd mind-guard-toolkit-main
   npm install

   # Install backend dependencies
   cd ../services/api-python
   pip install -r requirements.txt
   ```

4. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

5. **Test your changes**
   ```bash
   # Test frontend
   npm run build
   npm test

   # Test backend
   python basic_server.py
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m 'Add amazing feature'
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Describe your changes clearly
   - Reference any related issues
   - Wait for review and feedback

### Development Guidelines

- **Code Style**: Follow TypeScript/Python best practices
- **Testing**: Add tests for new functionality
- **Documentation**: Update README and code comments
- **Performance**: Consider impact on load times and user experience
- **Accessibility**: Ensure UI components are accessible

### Areas for Contribution

- ðŸŽ¨ **UI/UX Improvements**: Better animations, responsive design
- ðŸ” **Analysis Features**: New detection algorithms, better scoring
- ðŸ“± **Mobile Experience**: PWA features, offline capability
- ðŸŒ **Internationalization**: Multi-language support
- ðŸ§ª **Testing**: Unit tests, integration tests, E2E tests
- ðŸ“š **Documentation**: Tutorials, API documentation, examples

## ðŸ“„ License

MIT License - see [LICENSE](LICENSE) file for details.

## ðŸ™ Acknowledgments

- React and FastAPI communities for excellent frameworks
- shadcn/ui for beautiful component library
- TanStack Query for efficient state management
- All contributors and users of TrustNet

---

Built with â¤ï¸ for digital literacy and misinformation resistance
 
 
