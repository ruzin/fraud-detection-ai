import base64
import io
from PIL import Image
import PyPDF2
from typing import Tuple, Optional


class FileProcessor:
    
    @staticmethod
    def process_image(file_content: bytes, content_type: str) -> Tuple[str, Optional[str]]:
        try:
            image = Image.open(io.BytesIO(file_content))
            
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            
            base64_image = base64.b64encode(buffered.getvalue()).decode()
            
            return base64_image, None
            
        except Exception as e:
            return "", f"Error processing image: {str(e)}"
    
    @staticmethod
    def process_pdf(file_content: bytes) -> Tuple[str, Optional[str]]:
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            return text_content.strip(), None
            
        except Exception as e:
            return "", f"Error processing PDF: {str(e)}"
    
    @staticmethod
    def get_file_info(filename: str, content_type: str, file_size: int) -> dict:
        return {
            "filename": filename,
            "content_type": content_type,
            "file_size": file_size,
            "is_image": content_type.startswith('image/'),
            "is_pdf": content_type == 'application/pdf'
        }