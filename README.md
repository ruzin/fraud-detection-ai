# Document Categorization & Content Extraction System

A prototype system for document categorization and content extraction using LLM/VLM, with a focus on fraud prevention.

## Architecture

- **Backend**: FastAPI with document processing pipeline
- **Frontend**: Streamlit web interface  
- **LLM/VLM**: OpenRouter API (Claude 3.5 Sonnet)
- **File Processing**: PDF text extraction + image preprocessing

## Quick Start

### 1. Setup Environment
```bash
# Clone/navigate to project
cd ai-engineer-tech-test

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` with your OpenRouter API key and base url and ports as seen below:
```bash
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Backend Configuration  
BACKEND_HOST=localhost
BACKEND_PORT=8000

# Frontend Configuration
FRONTEND_PORT=8501
```

### 3. Start Services

**Terminal 1 - Backend:**
```bash
python start_backend.py
# Server will run on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
python start_frontend.py  
# UI will open at http://localhost:8501
```

### 4. Test the System
- Open http://localhost:8501
- Upload a document (PDF/PNG/JPEG)
- View categorization and extracted content

## Supported Categories

- **Invoice**: Bills, receipts, payment requests
- **Marketplace Listing Screenshot**: E-commerce product listings
- **Chat Screenshot**: Messaging apps, social media conversations  
- **Website Screenshot**: Web pages, website captures
- **Other**: Documents that don't fit above categories

## Key Assumptions
- **File Quality**: Documents are readable quality with clear text/images suitable for processing
- **Content Language**: Documents are primarily in English (Claude 3.5 Sonnet's primary language)
- **File Sources**: Files come from trusted sources, not adversarial or malicious content
- **Infrastructure**: Single-user localhost deployment with stable internet connectivity
- **API Availability**: OpenRouter and Claude 3.5 Sonnet remain accessible and functional
- **Categories**: The 5 predefined categories (invoice, marketplace listing, chat, website, other) cover majority of use cases
- **Performance**: 5-10 second processing time per document is acceptable for prototype
- **Security**: Local processing environment is secure, API keys are properly managed

## Design Decisions

### Technology Choices
- **FastAPI**: Fast, modern API framework with automatic documentation
- **Streamlit**: Rapid UI development for prototyping
- **OpenRouter**: Access to high-quality vision/language models
- **Pydantic**: Type safety and data validation

### Performance Optimizations
- **Image Preprocessing**: Thumbnail generation to reduce API payload
- **Async Processing**: Non-blocking document analysis
- **Error Handling**: Graceful degradation with fallback responses
- **Caching**: Potential for request/response caching (future enhancement)


## Known Limitations

1. **Processing Time**: Vision model calls can take 5-10 seconds
2. **File Size**: Large files may timeout or consume excessive tokens
3. **Model Hallucinations**: LLM may generate inaccurate extractions
4. **Rate Limits**: OpenRouter API has usage quotas
5. **Single File Processing**: No batch processing support

## Future Improvements
- Batch file processing
- Response caching layer
- model fine-tuning
- analytics dashboard
- Model router
- Response Caching with redis

## Processing Pipeline

1. **File Upload**: Accept PDF/image files via API
2. **Preprocessing**: 
   - Images: Resize, convert to JPEG, base64 encode
   - PDFs: Extract text content
3. **LLM Analysis**: Send to Claude 3.5 Sonnet for:
   - Category classification
   - Content extraction
   - Fraud risk assessment
4. **Response**: Return structured JSON with results

## Fraud Prevention Features

- **Risk Indicators**: Detects suspicious patterns and inconsistencies
- **Entity Extraction**: Identifies key information for verification
- **Confidence Scoring**: Provides reliability metrics
- **Quality Assessment**: Evaluates document clarity and completeness

## Model Configuration & Guardrails

### LLM Model Details
- **Model**: `anthropic/claude-3.5-sonnet` via OpenRouter
- **Capabilities**: Vision (images) + Text (PDFs) processing
- **Temperature**: `0.1` (low for consistent, deterministic output)
- **Max Tokens**: `2048` (prevents runaway responses)


### Guardrails & Error Handling

1. **JSON Structure Enforcement**
   - Regex extraction of JSON from model response
   - Handles cases where model adds explanatory text around JSON

2. **Fallback Response System**
   ```python
   # If JSON parsing fails
   {
       "category": "other",
       "confidence": 0.1,
       "fraud_risk_indicators": ["Analysis failed - manual review required"],
       "quality_score": 0.1
   }
   ```

3. **Error Response System**
   - All exceptions caught and returned as structured responses
   - No raw errors exposed to users
   - Processing errors flagged for manual review

4. **Input Validation**
   - File type restrictions (PDF, PNG, JPEG only)
   - File size limits via FastAPI
   - Content type verification

5. **Output Validation**
   - Category constrained to predefined set
   - Confidence scores validated (0.0-1.0 range)
   - Structured entity extraction format enforced