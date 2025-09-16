import openai
from typing import Dict, Any, Optional
from config import settings
import json
import re


class LLMClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )
        self.vision_model = "anthropic/claude-3.5-sonnet"
        self.text_model = "anthropic/claude-3.5-sonnet"
    
    async def analyze_document(self, content: str, is_image: bool = False, base64_image: str = None) -> Dict[str, Any]:
        try:
            system_prompt = """You are a document analysis expert specializing in categorization and content extraction for fraud prevention.

Analyze the provided document and return a JSON response with the following structure:
{
    "category": "one of: invoice, marketplace_listing_screenshot, chat_screenshot, website_screenshot, other",
    "confidence": "float between 0.0 and 1.0",
    "extracted_content": {
        "text": "extracted or transcribed text",
        "key_entities": {
            "company_names": [],
            "person_names": [],
            "amounts": [],
            "addresses": [],
            "phone_numbers": [],
            "email_addresses": [],
            "urls": [],
            "product_names": [],
            "other_relevant": []
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

Categories:
- invoice: Bills, receipts, payment requests
- marketplace_listing_screenshot: Product listings from e-commerce sites
- chat_screenshot: Screenshots of messaging apps, social media conversations
- website_screenshot: Screenshots of websites, web pages
- other: Documents that don't fit the above categories

Focus on fraud prevention - look for suspicious patterns, inconsistencies, or red flags."""

            if is_image and base64_image:
                messages = [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please analyze this document image."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
                model = self.vision_model
            else:
                messages = [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze this document text:\n\n{content}"
                    }
                ]
                model = self.text_model

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2048,
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return self._create_fallback_response(content)
                
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _create_fallback_response(self, content: str) -> Dict[str, Any]:
        return {
            "category": "other",
            "confidence": 0.1,
            "extracted_content": {
                "text": content[:1000] if content else "",
                "key_entities": {},
                "dates": [],
                "metadata": {
                    "document_type": "unknown",
                    "urgency_indicators": [],
                    "fraud_risk_indicators": ["Analysis failed - manual review required"],
                    "quality_score": 0.1
                }
            }
        }
    
    def _create_error_response(self, error: str) -> Dict[str, Any]:
        return {
            "category": "other",
            "confidence": 0.0,
            "extracted_content": {
                "text": "",
                "key_entities": {},
                "dates": [],
                "metadata": {
                    "document_type": "error",
                    "urgency_indicators": [],
                    "fraud_risk_indicators": [f"Processing error: {error}"],
                    "quality_score": 0.0
                }
            }
        }