# TrustNet Data Schemas

JSON Schema definitions for TrustNet data models.

## Claim Schema

The core data structure for user-submitted content to be analyzed.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://trustnet.dev/schemas/claim.json",
  "title": "Claim",
  "description": "A claim submitted for misinformation analysis",
  "type": "object",
  "required": ["id", "text", "language", "created_at", "source_type"],
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for the claim"
    },
    "text": {
      "type": "string",
      "minLength": 10,
      "maxLength": 10000,
      "description": "The text content to be analyzed"
    },
    "urls": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uri"
      },
      "maxItems": 5,
      "description": "URLs referenced in the claim"
    },
    "images": {
      "type": "array", 
      "items": {
        "type": "string",
        "format": "uri"
      },
      "maxItems": 3,
      "description": "Image URLs for visual content analysis"
    },
    "language": {
      "type": "string",
      "enum": ["hi", "bn", "te", "mr", "ta", "kn", "ml", "gu", "or", "pa", "ur", "en"],
      "description": "Primary language of the claim"
    },
    "script": {
      "type": "string",
      "enum": ["devanagari", "bengali", "telugu", "latin", "tamil", "kannada", "malayalam", "gujarati", "oriya", "gurmukhi", "arabic"],
      "description": "Writing script used"
    },
    "source_type": {
      "type": "string",
      "enum": ["social_media", "news", "messaging", "email", "web"],
      "description": "Platform or medium where claim originated"
    },
    "user_segment": {
      "type": "string", 
      "enum": ["journalist", "educator", "citizen", "fact_checker"],
      "description": "Category of user submitting the claim"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of claim submission"
    },
    "pii_redacted": {
      "type": "boolean",
      "default": false,
      "description": "Whether PII has been redacted from the text"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "processing", "completed", "failed"],
      "description": "Current processing status"
    }
  }
}
```

## Evidence Schema

Evidence snippets retrieved from trusted sources to support or refute claims.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://trustnet.dev/schemas/evidence.json",
  "title": "Evidence",
  "description": "Evidence snippet retrieved from trusted sources",
  "type": "object",
  "required": ["id", "claim_id", "snippet", "source_url", "relevance_score"],
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid"
    },
    "claim_id": {
      "type": "string", 
      "format": "uuid",
      "description": "Reference to the claim this evidence supports"
    },
    "snippet": {
      "type": "string",
      "maxLength": 1000,
      "description": "Extracted text snippet containing relevant information"
    },
    "source_url": {
      "type": "string",
      "format": "uri",
      "description": "URL of the original source document"
    },
    "source_title": {
      "type": "string",
      "maxLength": 200,
      "description": "Title of the source document"
    },
    "source_domain": {
      "type": "string",
      "description": "Domain name of the source"
    },
    "relevance_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Relevance score from search engine (0-1)"
    },
    "evidence_type": {
      "type": "string",
      "enum": ["supporting", "refuting", "contextual", "neutral"],
      "description": "How this evidence relates to the claim"
    },
    "extracted_at": {
      "type": "string",
      "format": "date-time",
      "description": "When this evidence was retrieved"
    },
    "language": {
      "type": "string",
      "description": "Language of the evidence snippet"
    }
  }
}
```

## Verdict Schema

Final assessment of claim accuracy aligned with ClaimReview schema.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://trustnet.dev/schemas/verdict.json", 
  "title": "Verdict",
  "description": "Final assessment of claim accuracy",
  "type": "object",
  "required": ["id", "claim_id", "rating", "rationale", "model_version"],
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid"
    },
    "claim_id": {
      "type": "string",
      "format": "uuid"
    },
    "rating": {
      "type": "string",
      "enum": ["True", "False", "Mixture", "Unproven", "Insufficient_Evidence"],
      "description": "Overall accuracy rating"
    },
    "confidence_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence in the verdict (0-1)"
    },
    "rationale": {
      "type": "string",
      "maxLength": 2000,
      "description": "Detailed explanation with evidence citations"
    },
    "evidence_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uuid"
      },
      "description": "References to supporting evidence"
    },
    "fact_check_matches": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "publisher": {"type": "string"},
          "url": {"type": "string", "format": "uri"},
          "rating": {"type": "string"},
          "date": {"type": "string", "format": "date"}
        }
      },
      "description": "Matching fact-check results"
    },
    "education_tips": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Media literacy tips for users"
    },
    "detection_scores": {
      "type": "object",
      "properties": {
        "misinformation_probability": {"type": "number"},
        "toxicity_score": {"type": "number"},
        "spam_score": {"type": "number"},
        "credibility_signal": {"type": "number"}
      },
      "description": "Various detection algorithm scores"
    },
    "model_version": {
      "type": "string",
      "description": "Version of the analysis model used"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

## Feedback Schema

User feedback on verdict accuracy for continuous improvement.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://trustnet.dev/schemas/feedback.json",
  "title": "Feedback", 
  "description": "User feedback on verdict accuracy",
  "type": "object",
  "required": ["verdict_id", "user_rating", "feedback_type"],
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid"
    },
    "verdict_id": {
      "type": "string",
      "format": "uuid"
    },
    "user_rating": {
      "type": "string",
      "enum": ["accurate", "inaccurate", "partially_accurate"],
      "description": "User's assessment of verdict quality"
    },
    "feedback_type": {
      "type": "string", 
      "enum": ["rating_disagreement", "missing_evidence", "poor_explanation", "factual_error"],
      "description": "Category of feedback issue"
    },
    "comments": {
      "type": "string",
      "maxLength": 1000,
      "description": "Optional detailed feedback"
    },
    "user_expertise": {
      "type": "string",
      "enum": ["expert", "knowledgeable", "general_public"],
      "description": "User's self-reported expertise level"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

## Firestore Collections

### Collection: `claims`
- Document ID: UUID
- Indexes: `language`, `source_type`, `created_at`, `status`

### Collection: `evidence`  
- Document ID: UUID
- Indexes: `claim_id`, `relevance_score`, `evidence_type`

### Collection: `verdicts`
- Document ID: UUID  
- Indexes: `claim_id`, `rating`, `confidence_score`, `created_at`

### Collection: `feedback`
- Document ID: UUID
- Indexes: `verdict_id`, `user_rating`, `feedback_type`, `created_at`
