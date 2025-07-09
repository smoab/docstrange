"""Image file processor with OCR capabilities."""

import os
import logging
from typing import Dict, Any

from .base import BaseProcessor
from ..result import ConversionResult
from ..exceptions import ConversionError, FileNotFoundError
from ..services.ocr_service import OCRServiceFactory

# Configure logging
logger = logging.getLogger(__name__)


class ImageProcessor(BaseProcessor):
    """Processor for image files (JPG, PNG, etc.) with OCR capabilities."""
    
    def __init__(self, preserve_layout: bool = True, include_images: bool = False, ocr_enabled: bool = False, use_markdownify: bool = None):
        super().__init__(preserve_layout, include_images, ocr_enabled, use_markdownify)
        self._ocr_service = None
    
    def can_process(self, file_path: str) -> bool:
        """Check if this processor can handle the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this processor can handle the file
        """
        if not os.path.exists(file_path):
            return False
        
        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        return ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif']
    
    def _get_ocr_service(self):
        """Get OCR service instance."""
        if self._ocr_service is None:
            self._ocr_service = OCRServiceFactory.create_service()
        return self._ocr_service
    
    def process(self, file_path: str) -> ConversionResult:
        """Process the image file and return a conversion result.
        
        Args:
            file_path: Path to the image file to process
            
        Returns:
            ConversionResult containing the processed content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ConversionError: If processing fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            from PIL import Image
            
            metadata = self.get_metadata(file_path)
            
            with Image.open(file_path) as img:
                # Extract image metadata
                image_info = {
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode,
                    "width": img.size[0],
                    "height": img.size[1]
                }
                
                # Create markdown content with image information
                content_parts = []
                content_parts.append(f"# Image: {os.path.basename(file_path)}")
                content_parts.append("")
                content_parts.append(f"**Format:** {image_info['format']}")
                content_parts.append(f"**Dimensions:** {image_info['width']} x {image_info['height']} pixels")
                content_parts.append(f"**Color Mode:** {image_info['mode']}")
                content_parts.append(f"**File Size:** {metadata.get('file_size', 'Unknown')} bytes")
                content_parts.append("")
                
                # Perform OCR if enabled
                if self.ocr_enabled:
                    ocr_service = self._get_ocr_service()
                    ocr_text = ocr_service.extract_text_with_layout(file_path)
                    
                    if ocr_text:
                        content_parts.append("## Extracted Text (OCR)")
                        content_parts.append("")
                        content_parts.append(ocr_text)
                        content_parts.append("")
                        metadata.update({
                            "ocr_performed": True,
                            "ocr_text_length": len(ocr_text)
                        })
                    else:
                        content_parts.append("*OCR was performed but no text was detected in this image.*")
                        metadata.update({
                            "ocr_performed": True,
                            "ocr_text_length": 0
                        })
                else:
                    content_parts.append("*This image contains visual content that cannot be converted to text without OCR.*")
                    content_parts.append("*Enable OCR processing to extract text from this image.*")
                    metadata.update({
                        "ocr_performed": False
                    })
                
                content = "\n".join(content_parts)
                
                metadata.update({
                    "image_info": image_info,
                    "converter": "pillow"
                })
                
                return ConversionResult(content, metadata)
                
        except ImportError:
            raise ConversionError("Pillow is required for image processing. Install it with: pip install Pillow")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, ConversionError)):
                raise
            raise ConversionError(f"Failed to process image file {file_path}: {str(e)}")
    
    @staticmethod
    def predownload_ocr_models():
        """Pre-download OCR models by running a dummy prediction."""
        try:
            from llm_converter.services.ocr_service import OCRServiceFactory
            ocr_service = OCRServiceFactory.create_service()
            # Create a blank image for testing
            from PIL import Image
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                img = Image.new('RGB', (100, 100), color='white')
                img.save(tmp.name)
                ocr_service.extract_text_with_layout(tmp.name)
                os.unlink(tmp.name)
            print("OCR models pre-downloaded and cached.")
        except Exception as e:
            print(f"Failed to pre-download OCR models: {e}") 