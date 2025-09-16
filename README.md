# Document Categorization & Content Extraction System

A prototype system for document categorization and content extraction using LLM/VLM, with a focus on fraud prevention.

## Architecture

- **Backend**: FastAPI with document processing pipeline
- **Frontend**: Streamlit web interface  
- **LLM/VLM**: OpenRouter API (Claude 3.5 Sonnet)
- **File Processing**: PDF text extraction + image preprocessing

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit UI   │ ──►│   FastAPI API   │ ──►│  OpenRouter LLM │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │ File Processing │
                       │ (PDF/Images)    │
                       └─────────────────┘
```
## Project Structure

```
fraud-detection-ai/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── document_processor.py # Main processing logic
│   ├── file_processor.py    # File handling utilities  
│   ├── llm_client.py        # OpenRouter integration
│   └── config.py            # Configuration management
├── frontend/
│   └── app.py               # Streamlit interface
├── shared/
│   └── models.py            # Pydantic data models
├── file examples/           # Test input documents
├── output/                  # Example JSON output files
│   ├── job_offer.json       # Job posting analysis result
│   └── market_place_listing.json # Marketplace listing result
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── start_backend.py         # Backend startup script
└── start_frontend.py        # Frontend startup script
```

## Quick Start

### 1. Setup Environment
```bash
# Clone/navigate to project
cd ai-engineer-tech-test

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### 2. Configure API Key
Update `.env` with your OpenRouter API key:
```bash
OPENROUTER_API_KEY=your_key_here
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

### Short Term
- [ ] Batch file processing
- [ ] Processing progress indicators  
- [ ] Result export (CSV, Excel)
- [ ] File upload validation improvements

### Medium Term  
- [ ] Response caching layer
- [ ] Multiple model comparison
- [ ] Custom extraction templates
- [ ] Advanced fraud detection rules

### Long Term
- [ ] Real-time processing webhooks
- [ ] ML model fine-tuning
- [ ] Integration with document management systems
- [ ] Advanced analytics dashboard

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

### System Prompt
The model uses a structured prompt focused on fraud prevention:

```
You are a document analysis expert specializing in categorization and content extraction for fraud prevention.

Analyze the provided document and return a JSON response with the following structure:
{
    "category": "one of: invoice, marketplace_listing_screenshot, chat_screenshot, website_screenshot, other",
    "confidence": "float between 0.0 and 1.0",
    "extracted_content": {
        "text": "extracted or transcribed text",
        "key_entities": {
            "company_names": [], "person_names": [], "amounts": [],
            "addresses": [], "phone_numbers": [], "email_addresses": [],
            "urls": [], "product_names": [], "other_relevant": []
        },
        "dates": [],
        "metadata": {
            "document_type": "more specific type if applicable",
            "urgency_indicators": [],
            "fraud_risk_indicators": [],
            "quality_score": "float between 0.0 and 1.0"
        }
    }
}

Focus on fraud prevention - look for suspicious patterns, inconsistencies, or red flags.
```

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