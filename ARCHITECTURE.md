# TrustNet: AI-Powered Misinformation Detection System

## Executive Summary

**TrustNet** is an AI-powered misinformation detection system for India that uses Google Cloud services to analyze content, retrieve evidence from trusted sources, and educate users on media literacy. The platform serves journalists, fact-checkers, educators, and citizens with transparent explanations and grounded evidence to combat false narratives across multiple Indian languages.

## High-Level Reference Architecture

The system follows a **serverless, event-driven architecture** using managed Google Cloud services for automatic scaling and security. Content flows through parallel validation pipelines before ML-powered analysis generates grounded explanations with educational context.

**Architecture Flow Sequence:**
1. User submits content via REST API to Cloud Run gateway
2. DLP API redacts PII; Web Risk validates URLs 
3. Pub/Sub triggers parallel workers for evidence retrieval and fact-checking
4. Vertex AI Search extracts relevant evidence snippets from trusted corpora
5. Fact Check Tools API searches for existing ClaimReview records
6. Perspective API scores content quality and toxicity signals
7. Vertex AI LLM generates grounded analysis with retrieved evidence
8. Verdict persisted to Firestore with full citation chain
9. Response returned with transparent rationales and education tips

## Service-by-Service Design

### Cloud Run Services
- **API Gateway**: Stateless REST endpoints, auto-scaling 0-1000 instances
- **Analysis Workers**: Content processing with Vertex AI integration
- **Evidence Workers**: Async retrieval and source indexing jobs
- **Webhook Handlers**: External integration callbacks and notifications

### Pub/Sub Topics
- **content-analysis**: Triggers ML pipelines for submitted claims
- **evidence-retrieval**: Async document search and snippet extraction  
- **fact-check-lookup**: External API integration with retry policies
- **verdict-updates**: Real-time notifications for UI components

### Firestore Collections
- **claims**: User submissions with metadata and language detection
- **evidence**: Retrieved snippets with source URLs and relevance scores
- **verdicts**: Final assessments aligned to ClaimReview schema
- **feedback**: User interactions and accuracy corrections

### Vertex AI Components
- **Search Index**: Trusted sources (PDFs, websites, structured data)
- **LLM Models**: Gemini for analysis and explanation generation
- **Classification Models**: Custom fine-tuned models for Indian misinformation patterns

### Integration Adapters
- **Fact Check Tools**: ClaimReview search with rate limit handling
- **Web Risk**: URL reputation and malware detection
- **Perspective**: Toxicity and spam scoring for credibility signals
- **DLP**: PII detection and redaction before storage

## Repository Layout

```
trustnet/
├── apps/                      # Frontend applications and user interfaces
│   ├── web/                   # React web dashboard for fact-checkers
│   ├── extension/             # Browser extension for real-time checking
│   └── mobile/                # React Native app for mobile users
├── services/                  # Backend microservices on Cloud Run
│   ├── api/                   # REST API gateway and authentication
│   ├── workers/               # Background processing services
│   └── webhooks/              # External integration callbacks
├── ml/                        # Machine learning components and pipelines
│   ├── retrieval/             # Vertex AI Search configuration and indexing
│   ├── prompts/               # LLM prompt templates and versions
│   ├── pipelines/             # Training and evaluation workflows
│   └── eval/                  # Model testing and performance metrics
├── integrations/              # External API adapters and clients
│   ├── factcheck/             # Fact Check Tools API integration
│   ├── webrisk/               # Web Risk API for URL safety
│   ├── perspective/           # Perspective API for content quality
│   └── dlp/                   # DLP API for PII detection
├── data/                      # Data schemas and seed content
│   ├── schemas/               # JSON schemas for data validation
│   ├── seeds/                 # Initial trusted source corpus
│   └── examples/              # Sample requests and responses
├── infra/                     # Infrastructure as Code and deployment
│   ├── terraform/             # Google Cloud resource definitions
│   ├── ci/                    # Cloud Build pipelines and tests
│   └── monitoring/            # Logging and alerting configurations
├── docs/                      # Documentation and specifications
│   ├── architecture/          # System design and decision records
│   ├── api/                   # OpenAPI specifications
│   └── guides/                # User and developer guides
└── scripts/                   # Deployment and maintenance utilities
    ├── deploy/                # Automated deployment commands
    ├── data/                  # Data migration and seeding scripts
    └── monitoring/            # Health checks and diagnostic tools
```

## Core Data Contracts

### Claim Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "text", "language", "created_at", "source_type"],
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "text": {"type": "string", "maxLength": 10000},
    "urls": {"type": "array", "items": {"type": "string", "format": "uri"}},
    "images": {"type": "array", "items": {"type": "string", "format": "uri"}},
    "language": {"type": "string", "enum": ["hi", "bn", "te", "mr", "ta", "kn", "ml", "gu", "or", "pa", "ur", "en"]},
    "script": {"type": "string", "enum": ["devanagari", "bengali", "telugu", "latin", "tamil", "kannada", "malayalam", "gujarati", "oriya", "gurmukhi", "arabic"]},
    "source_type": {"type": "string", "enum": ["social_media", "news", "messaging", "email", "web"]},
    "user_segment": {"type": "string", "enum": ["journalist", "educator", "citizen", "fact_checker"]},
    "created_at": {"type": "string", "format": "date-time"},
    "pii_redacted": {"type": "boolean", "default": false}
  }
}
```

### Evidence Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "claim_id", "snippet", "source_url", "relevance_score"],
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "claim_id": {"type": "string", "format": "uuid"},
    "snippet": {"type": "string", "maxLength": 1000},
    "source_url": {"type": "string", "format": "uri"},
    "source_title": {"type": "string", "maxLength": 200},
    "source_domain": {"type": "string"},
    "relevance_score": {"type": "number", "minimum": 0, "maximum": 1},
    "evidence_type": {"type": "string", "enum": ["supporting", "refuting", "contextual", "neutral"]},
    "extracted_at": {"type": "string", "format": "date-time"},
    "language": {"type": "string"}
  }
}
```

### Verdict Schema (ClaimReview Aligned)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "claim_id", "rating", "rationale", "model_version"],
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "claim_id": {"type": "string", "format": "uuid"},
    "rating": {"type": "string", "enum": ["True", "False", "Mixture", "Unproven", "Insufficient_Evidence"]},
    "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
    "rationale": {"type": "string", "maxLength": 2000},
    "evidence_ids": {"type": "array", "items": {"type": "string", "format": "uuid"}},
    "fact_check_matches": {"type": "array", "items": {"type": "object"}},
    "education_tips": {"type": "array", "items": {"type": "string"}},
    "detection_scores": {
      "type": "object",
      "properties": {
        "misinformation_probability": {"type": "number"},
        "toxicity_score": {"type": "number"},
        "spam_score": {"type": "number"}
      }
    },
    "model_version": {"type": "string"},
    "created_at": {"type": "string", "format": "date-time"}
  }
}
```

### Feedback Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["verdict_id", "user_rating", "feedback_type"],
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "verdict_id": {"type": "string", "format": "uuid"},
    "user_rating": {"type": "string", "enum": ["accurate", "inaccurate", "partially_accurate"]},
    "feedback_type": {"type": "string", "enum": ["rating_disagreement", "missing_evidence", "poor_explanation", "factual_error"]},
    "comments": {"type": "string", "maxLength": 1000},
    "user_expertise": {"type": "string", "enum": ["expert", "knowledgeable", "general_public"]},
    "created_at": {"type": "string", "format": "date-time"}
  }
}
```

## API Specification

### Core Endpoints

```yaml
openapi: 3.1.0
info:
  title: TrustNet API
  version: 1.0.0
  description: AI-powered misinformation detection and fact-checking

paths:
  /v1/analyze:
    post:
      summary: Submit content for misinformation analysis
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [text]
              properties:
                text:
                  type: string
                  maxLength: 10000
                urls:
                  type: array
                  items:
                    type: string
                    format: uri
                language:
                  type: string
                  enum: [hi, bn, te, mr, ta, kn, ml, gu, or, pa, ur, en]
                priority:
                  type: string
                  enum: [low, normal, high]
                  default: normal
      responses:
        '200':
          description: Analysis completed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AnalysisResult'
        '202':
          description: Analysis queued for processing
        '400':
          description: Invalid request format
        '429':
          description: Rate limit exceeded

  /v1/claims/{claimId}:
    get:
      summary: Retrieve claim analysis results
      parameters:
        - name: claimId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Claim found
        '404':
          description: Claim not found

  /v1/feedback:
    post:
      summary: Submit user feedback on verdict accuracy
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Feedback'
      responses:
        '201':
          description: Feedback recorded

components:
  schemas:
    AnalysisResult:
      type: object
      properties:
        claim_id:
          type: string
          format: uuid
        verdict:
          $ref: '#/components/schemas/Verdict'
        processing_time_ms:
          type: integer
        grounding_coverage:
          type: number
          minimum: 0
          maximum: 1
```

## Retrieval Plan

### Vertex AI Search Configuration

**Index Types:**
- **Structured Data**: Fact-check databases, government announcements, verified statistics
- **Unstructured Documents**: Research papers, news articles, expert reports stored in Cloud Storage
- **Website Crawl**: Trusted news domains, health authorities, financial regulators

**Update Schedule:**
- Real-time: Government feeds, breaking news from trusted sources
- Daily: Research repositories, fact-check databases
- Weekly: Academic papers, policy documents

**Scoring and Ranking:**
- **Relevance**: Semantic similarity to claim using embedding models
- **Authority**: Domain reputation and source credibility scores  
- **Recency**: Time-decay for news events, evergreen for scientific facts
- **Language Match**: Prioritize content in same language as query

**Extractive Answer Generation:**
The system retrieves 3-5 most relevant snippets (100-200 words each) with source URLs, which are then injected into LLM prompts with explicit citation instructions: "Base your analysis only on the provided evidence snippets. Quote directly and include [Source X] citations for each claim."

## Reasoning and Generation

### Prompt Templates

**Risk Classification Prompt:**
```
You are an expert fact-checker analyzing content for potential misinformation. 

CLAIM: {user_content}
EVIDENCE: {retrieved_snippets}
FACT_CHECK_MATCHES: {factcheck_api_results}

Classify this claim's accuracy using only the provided evidence:
- TRUE: Fully supported by credible sources
- FALSE: Directly contradicted by evidence  
- MIXTURE: Contains both accurate and inaccurate elements
- UNPROVEN: Insufficient evidence to verify
- INSUFFICIENT_EVIDENCE: Not enough reliable sources found

Provide your reasoning with direct quotes from evidence sources.
```

**Educational Explanation Prompt:**
```
Based on the misinformation analysis, educate the user on media literacy:

CLAIM: {user_content}  
VERDICT: {classification_result}
EVIDENCE: {grounded_snippets}

Generate 3-5 educational tips that help users:
1. Identify manipulation techniques used (if any)
2. Recognize credibility indicators in sources
3. Apply critical thinking to similar claims
4. Find authoritative sources for verification

Ground each tip in the specific evidence found. Use simple language appropriate for general audiences.
```

**Citation Integration:**
All generated explanations must include verbatim quotes from retrieved evidence with format: *"According to [Source Name], 'direct quote from evidence snippet.'"* This ensures every claim in the explanation can be traced back to a specific source document indexed in Vertex AI Search.

## Safety and Privacy

### URL Safety via Web Risk
**Threat Types Checked:**
- MALWARE: Sites hosting malicious software
- SOCIAL_ENGINEERING: Phishing and deceptive sites  
- UNWANTED_SOFTWARE: Sites with PUPs or adware
- POTENTIALLY_HARMFUL_APPLICATION: Suspicious mobile apps

URLs flagged by Web Risk are quarantined and not processed for content analysis, protecting users from security threats disguised as information sources.

### Content Quality via Perspective
**Attributes Scored:**
- TOXICITY: Harmful or offensive language detection
- SEVERE_TOXICITY: Extremely harmful content identification  
- IDENTITY_ATTACK: Targeting individuals or groups
- INSULT: Personal attacks and name-calling
- PROFANITY: Explicit language detection
- THREAT: Direct or implied threats

Content with toxicity scores >0.8 receives reduced credibility weighting, as toxic language often correlates with misinformation patterns.

### DLP Redaction Policies
**InfoTypes Detected:**
- PERSON_NAME: Individual names for anonymization
- PHONE_NUMBER: Contact information protection
- EMAIL_ADDRESS: Personal email redaction
- CREDIT_CARD_NUMBER: Financial data protection
- INDIA_PAN: Indian tax ID numbers
- INDIA_AADHAAR: Aadhaar number detection and redaction

**Transformation Methods:**
- **Redaction**: Replace with `[REDACTED]` for display
- **Tokenization**: Replace with consistent tokens for analysis
- **Crypto Hashing**: One-way hashing for deduplication without storage

All PII is redacted before storage in Firestore and before inclusion in LLM prompts to ensure privacy compliance.

## Evaluation Framework

### Offline Test Set Design
- **Ground Truth Dataset**: 1000+ manually verified claims across Indian languages
- **Domain Coverage**: Health misinformation, financial scams, political claims, communal rumors
- **Language Distribution**: 40% Hindi, 20% English, 40% other Indian languages
- **Difficulty Levels**: Clear true/false, nuanced contexts, satirical content

### Grounding Faithfulness Checks
- **Citation Accuracy**: Verify each claim in explanation matches retrieved evidence
- **Hallucination Detection**: Flag generated content not supported by evidence
- **Source Attribution**: Ensure all quotes properly attributed to source URLs
- **Evidence Coverage**: Measure percentage of explanation grounded in retrieved snippets

### Performance SLOs
- **Detection Accuracy**: >85% precision/recall on test set
- **Grounding Coverage**: >80% of explanation content linked to evidence
- **Latency**: P95 <3 seconds end-to-end for text analysis
- **Cost**: <$0.10 per analysis request at scale
- **Uptime**: 99.9% API availability with graceful degradation

### Human-in-the-Loop Review
Expert fact-checkers review 5% of high-confidence verdicts and 100% of borderline cases (confidence <0.7) to maintain quality and identify systematic errors for model improvement.

## Deployment Architecture

### Container Build Pipeline
```bash
# Cloud Build configuration
gcloud builds submit --config=cloudbuild.yaml

# Build steps:
# 1. Multi-stage Docker build with security scanning
# 2. Unit and integration test execution  
# 3. Vulnerability assessment with Binary Authorization
# 4. Push to Artifact Registry with attestation
# 5. Deploy to Cloud Run with traffic splitting
```

### Environment Configuration
**Minimum IAM Roles:**
- **API Service Account**: `run.invoker`, `firestore.user`, `aiplatform.user`
- **Worker Service Account**: `pubsub.subscriber`, `storage.objectViewer`, `dlp.user`
- **Pipeline Service Account**: `vertex.user`, `storage.admin`, `pubsub.admin`

**Required Environment Variables:**
```bash
PROJECT_ID=trustnet-prod
FIRESTORE_DATABASE=trustnet-db
VERTEX_SEARCH_INDEX=evidence-corpus
FACT_CHECK_API_KEY=projects/${PROJECT_ID}/secrets/factcheck-key
WEB_RISK_API_KEY=projects/${PROJECT_ID}/secrets/webrisk-key
```

### Terraform Deployment
```hcl
# Core infrastructure
module "trustnet_infrastructure" {
  source = "./terraform/modules/trustnet"
  
  project_id = var.project_id
  region = "asia-south1"
  
  # Cloud Run configuration
  api_cpu = "2"
  api_memory = "4Gi"
  api_max_instances = 1000
  
  # Pub/Sub topics
  enable_dlq = true
  message_retention = "7d"
  
  # Firestore
  database_type = "firestore-native"
  location_id = "asia-south1"
}
```

## Operations and Monitoring

### Key Performance Indicators
- **Request Latency**: P95 response time across all endpoints
- **Error Rate**: 5XX errors per minute with alert thresholds
- **Grounding Coverage**: Percentage of responses with cited evidence
- **Cost per Request**: Real-time cost tracking with budget alerts
- **API Quota Usage**: Monitoring for Vertex AI, Fact Check Tools limits

### Alerting Policies
```yaml
# Cloud Monitoring alert policies
alert_policies:
  - name: "High Error Rate"
    condition: "error_rate > 5% for 5 minutes"
    notification: "pagerduty-critical"
  
  - name: "Latency Degradation"  
    condition: "p95_latency > 5s for 10 minutes"
    notification: "slack-engineering"
    
  - name: "Cost Spike"
    condition: "daily_cost > $500"
    notification: "email-finance"
```

### Retry and Backoff Policies
- **Pub/Sub**: Exponential backoff with max 7 retries
- **External APIs**: Circuit breaker pattern with 30s cooldown
- **Firestore**: Automatic retry with jitter for write conflicts
- **Dead Letter Queues**: Manual review for messages failing >7 attempts

## Accessibility and Localization

### Indian Language Support
**Primary Languages**: Hindi, Bengali, Telugu, Marathi, Tamil, Kannada, Malayalam, Gujarati, Odia, Punjabi, Urdu
**Script Handling**: Unicode normalization for Devanagari, Bengali, Tamil, Telugu scripts
**Transliteration**: Roman to native script conversion for code-mixed content
**Font Support**: Web fonts for regional scripts with fallback chains

### Mobile-First Design
- **Progressive Web App**: Offline-capable with Service Workers
- **Data Optimization**: Image compression, lazy loading, critical CSS inlining
- **Network Awareness**: Graceful degradation on 2G/3G connections  
- **Battery Optimization**: Minimize background processing, efficient animations

### WCAG AA Compliance
- **Color Contrast**: Minimum 4.5:1 ratio for text, 3:1 for UI elements
- **Keyboard Navigation**: Full functionality without mouse interaction
- **Screen Reader**: Semantic HTML, ARIA labels, live regions for dynamic updates
- **Font Scaling**: Support for 200% zoom without horizontal scrolling

## Risk Register and Mitigations

### Model Hallucinations
**Risk**: LLM generates false explanations not grounded in evidence
**Mitigation**: Strict prompt engineering requiring citations, post-processing validation, human review for low-confidence outputs

### Dataset Drift
**Risk**: Training data becomes outdated, affecting accuracy on emerging misinformation patterns  
**Mitigation**: Continuous evaluation pipeline, monthly model retraining, A/B testing of model versions

### Adversarial Prompts
**Risk**: Users attempt to manipulate system with crafted inputs
**Mitigation**: Input sanitization, prompt injection detection, rate limiting per user, abuse monitoring

### False Positives Impact
**Risk**: Incorrectly flagging legitimate content damages platform credibility
**Mitigation**: Conservative thresholds, uncertainty communication, easy feedback mechanisms, expert review workflows

### Source Bias
**Risk**: Evidence corpus contains systematic biases affecting verdict quality
**Mitigation**: Diverse source inclusion criteria, regular bias audits, transparent source attribution, user education on source limitations

### Cost Spikes
**Risk**: Viral content creates unexpected API usage surges
**Mitigation**: Budget alerts, usage quotas, auto-scaling limits, cost-optimized fallback modes

### Abuse Prevention
**Risk**: System used to legitimize false information through selective querying
**Mitigation**: Usage analytics, repeat query detection, verdict transparency, public audit logs

## Roadmap and Feature Evolution

### MVP Phase
**Core Features**:
- Text-only misinformation detection for Hindi and English
- Basic evidence retrieval from curated source corpus  
- Simple web interface for fact-checker teams
- Integration with Google Fact Check Tools API
- Firestore-based verdict storage and retrieval

**Success Metrics**:
- Process 1000 claims/day with >80% accuracy
- Average response time <5 seconds  
- User satisfaction score >4/5 from pilot fact-checkers

### Beta Phase  
**Enhanced Capabilities**:
- Multi-language support for 5+ Indian languages
- Image analysis via URL reference and OCR
- Browser extension for real-time social media checking
- Perspective API integration for toxicity scoring
- Advanced evidence ranking and snippet extraction

**Scaling Targets**:
- Support 10,000 requests/day across all languages
- Expand to 8 major Indian languages with cultural context
- Onboard 3 major fact-checking organizations

### General Availability
**Production Features**:
- Real-time processing with <2 second latency
- Mobile applications for Android/iOS
- API partnerships with social media platforms
- Advanced ML models fine-tuned on Indian misinformation patterns  
- Comprehensive analytics dashboard for media literacy research

**Impact Goals**:
- Serve 100,000+ daily users across India
- Integration with major news platforms and social networks
- Measurable reduction in misinformation spread among user communities
- Educational impact through improved media literacy scores

## Assumptions and Open Questions

### Technical Assumptions
- **Vertex AI Search** provides sufficient extractive answer quality for Indian language content
- **Google Fact Check Tools API** coverage will improve for regional Indian fact-checkers over time
- **Cloud Run** auto-scaling can handle viral content traffic spikes without manual intervention
- **Firestore** document limits (1MB) sufficient for storing claim analysis with evidence

### Data and Content Assumptions  
- Trusted source corpus can be curated and maintained with sufficient breadth for Indian context
- Translation quality between Indian languages adequate for cross-language evidence matching
- **Perspective API** toxicity models perform adequately on Indian language content and cultural context

### Business and Policy Questions
- **User consent** requirements for storing analyzed content under Indian data protection regulations
- **Liability concerns** when system incorrectly flags legitimate content or misses actual misinformation
- **Revenue model** sustainability for providing free public service while covering Google Cloud costs
- **Editorial guidelines** for determining "trusted sources" in politically sensitive contexts

### Open Technical Questions
- **Evidence freshness** optimal update frequency for different source types (news vs academic papers)
- **Citation granularity** whether sentence-level or paragraph-level attribution provides better user experience  
- **Multilingual model** performance trade-offs between language-specific vs unified models
- **Caching strategy** for repeat queries on viral content to optimize cost and latency
- **Human oversight** optimal sampling rate for manual review to maintain quality without bottlenecking scale
