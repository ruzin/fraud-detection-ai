import sys
import os
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.models import ProcessingResult, DocumentCategory
from file_processor import FileProcessor
from llm_client import LLMClient


class DocumentProcessor:
    def __init__(self):
        self.file_processor = FileProcessor()
        self.llm_client = LLMClient()
    
    async def process_document(
        self, 
        file_content: bytes, 
        filename: str, 
        content_type: str, 
        file_id: str
    ) -> ProcessingResult:
        try:
            file_info = self.file_processor.get_file_info(
                filename, content_type, len(file_content)
            )
            
            if file_info["is_image"]:
                base64_image, error = self.file_processor.process_image(
                    file_content, content_type
                )
                if error:
                    raise Exception(error)
                
                analysis = await self.llm_client.analyze_document(
                    content="", 
                    is_image=True, 
                    base64_image=base64_image
                )
                
            elif file_info["is_pdf"]:
                text_content, error = self.file_processor.process_pdf(file_content)
                if error:
                    raise Exception(error)
                
                analysis = await self.llm_client.analyze_document(
                    content=text_content, 
                    is_image=False
                )
                
            else:
                raise Exception(f"Unsupported file type: {content_type}")
            
            category = self._map_category(analysis.get("category", "other"))
            confidence = float(analysis.get("confidence", 0.0))
            extracted_content = analysis.get("extracted_content", {})
            
            extracted_content["file_info"] = file_info
            
            return ProcessingResult(
                file_id=file_id,
                filename=filename,
                category=category,
                confidence=confidence,
                extracted_content=extracted_content,
                processing_time=0.0
            )
            
        except Exception as e:
            return ProcessingResult(
                file_id=file_id,
                filename=filename,
                category=DocumentCategory.OTHER,
                confidence=0.0,
                extracted_content={"error_details": str(e)},
                processing_time=0.0,
                error=str(e)
            )
    
    def _map_category(self, category_str: str) -> DocumentCategory:
        category_mapping = {
            "invoice": DocumentCategory.INVOICE,
            "marketplace_listing_screenshot": DocumentCategory.MARKETPLACE_LISTING_SCREENSHOT,
            "chat_screenshot": DocumentCategory.CHAT_SCREENSHOT,
            "website_screenshot": DocumentCategory.WEBSITE_SCREENSHOT,
            "other": DocumentCategory.OTHER
        }
        return category_mapping.get(category_str.lower(), DocumentCategory.OTHER)