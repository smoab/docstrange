"""PDF file processor with OCR support for scanned PDFs."""

import os
import logging
import tempfile
from typing import Dict, Any, List, Tuple

from .base import BaseProcessor
from .image_processor import ImageProcessor
from ..result import ConversionResult
from ..exceptions import ConversionError, FileNotFoundError
from ..config import InternalConfig

# Configure logging
logger = logging.getLogger(__name__)


class PDFProcessor(BaseProcessor):
    """Processor for PDF files using PDF-to-image conversion with OCR."""
    
    def __init__(self, preserve_layout: bool = True, include_images: bool = False, ocr_enabled: bool = False, use_markdownify: bool = None):
        super().__init__(preserve_layout, include_images, ocr_enabled, use_markdownify)
        self._image_processor = ImageProcessor(
            preserve_layout=preserve_layout,
            include_images=include_images,
            ocr_enabled=ocr_enabled,
            use_markdownify=use_markdownify
        )
    
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
        return ext == '.pdf'
    
    def process(self, file_path: str) -> ConversionResult:
        """Process the PDF file and return a conversion result.
        
        Args:
            file_path: Path to the PDF file to process
            
        Returns:
            ConversionResult containing the processed content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ConversionError: If processing fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Convert PDF pages to images and process each page
        return self._process_pdf_to_images(file_path)
    
    def _process_pdf_to_images(self, file_path: str) -> ConversionResult:
        """Process PDF by converting pages to images and using ImageProcessor logic."""
        try:
            import fitz  # PyMuPDF
            
            logger.info(f"Opening PDF with PyMuPDF: {file_path}")
            doc = fitz.open(file_path)
            logger.info(f"PDF opened successfully. Pages: {len(doc)}")
            
            content_parts = []
            page_count = len(doc)
            total_text_length = 0
            pages_with_text = 0
            
            # Get PDF metadata
            metadata = self.get_metadata(file_path)
            metadata.update({
                "page_count": page_count,
                "converter": "pdf_to_image_ocr"
            })
            
            for page_num in range(page_count):
                logger.info(f"Processing page {page_num + 1} of {page_count}")
                
                # Convert page to image
                image_path = self._convert_page_to_image(doc, page_num)
                
                if image_path and os.path.exists(image_path):
                    try:
                        # Process the image using ImageProcessor logic
                        page_result = self._image_processor.process(image_path)
                        
                        if page_result and page_result.content:
                            # Extract the OCR text from the image result
                            ocr_text = self._extract_ocr_text_from_result(page_result)
                            
                            if ocr_text:
                                pages_with_text += 1
                                total_text_length += len(ocr_text)
                                
                                # Format as page content
                                page_content = self._format_page_content(ocr_text, page_num + 1)
                                content_parts.append(page_content)
                                
                                logger.info(f"Page {page_num + 1} processed successfully, text length: {len(ocr_text)}")
                            else:
                                logger.warning(f"No OCR text extracted from page {page_num + 1}")
                                content_parts.append(f"\n## Page {page_num + 1}\n\n*No text detected on this page.*\n")
                        else:
                            logger.warning(f"Image processing failed for page {page_num + 1}")
                            content_parts.append(f"\n## Page {page_num + 1}\n\n*Image processing failed for this page.*\n")
                    
                    finally:
                        # Clean up temporary image file
                        if os.path.exists(image_path):
                            os.unlink(image_path)
                            logger.debug(f"Cleaned up temporary image: {image_path}")
                else:
                    logger.error(f"Failed to convert page {page_num + 1} to image")
                    content_parts.append(f"\n## Page {page_num + 1}\n\n*Failed to convert page to image.*\n")
            
            logger.info(f"PDF processing complete. Pages with text: {pages_with_text}/{page_count}")
            doc.close()
            
            content = "\n\n".join(content_parts)
            metadata.update({
                "pages_with_text": pages_with_text,
                "total_text_length": total_text_length
            })
            
            return ConversionResult(content, metadata)
            
        except ImportError:
            raise ImportError("PyMuPDF is required for PDF processing. Install it with: pip install PyMuPDF")
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise ConversionError(f"PDF processing failed: {str(e)}")
    
    def _convert_page_to_image(self, doc, page_num: int) -> str:
        """Convert a PDF page to an image file.
        
        Args:
            doc: PyMuPDF document object
            page_num: Page number (0-based)
            
        Returns:
            Path to the temporary image file
        """
        try:
            import fitz  # PyMuPDF
            
            page = doc.load_page(page_num)
            
            # Use configuration for image quality
            dpi = getattr(InternalConfig, 'pdf_image_dpi', 300)
            scale = getattr(InternalConfig, 'pdf_image_scale', 2.0)
            
            # Calculate matrix for desired DPI
            mat = fitz.Matrix(scale, scale)
            
            # Convert page to pixmap
            pix = page.get_pixmap(matrix=mat)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                pix.save(tmp_file.name)
                logger.debug(f"Page {page_num + 1} converted to image: {tmp_file.name}")
                return tmp_file.name
                
        except Exception as e:
            logger.error(f"Failed to convert page {page_num + 1} to image: {e}")
            return None
    
    def _extract_ocr_text_from_result(self, result: ConversionResult) -> str:
        """Extract OCR text from ImageProcessor result.
        
        Args:
            result: ConversionResult from ImageProcessor
            
        Returns:
            Extracted OCR text
        """
        try:
            content = result.content
            
            # Look for OCR section in the content
            if "## Extracted Text (OCR)" in content:
                # Extract text after the OCR header
                parts = content.split("## Extracted Text (OCR)")
                if len(parts) > 1:
                    ocr_section = parts[1]
                    # Remove any remaining headers and clean up
                    lines = ocr_section.split('\n')
                    text_lines = []
                    in_ocr_text = False
                    
                    for line in lines:
                        if line.strip() == "":
                            continue
                        elif line.startswith("##"):
                            # Stop at next header
                            break
                        else:
                            text_lines.append(line)
                    
                    return '\n'.join(text_lines).strip()
            
            # If no OCR section found, return the full content
            return content
            
        except Exception as e:
            logger.error(f"Failed to extract OCR text from result: {e}")
            return ""
    
    def _format_page_content(self, text: str, page_num: int) -> str:
        """Format page content as markdown.
        
        Args:
            text: Extracted text
            page_num: Page number
            
        Returns:
            Formatted markdown content
        """
        if not text.strip():
            return f"\n## Page {page_num}\n\n*This page appears to be empty or contains no extractable text.*\n"
        
        # Build markdown content
        content_parts = [f"## Page {page_num}"]
        content_parts.append("")
        content_parts.append(text)
        content_parts.append("")
        
        return '\n'.join(content_parts)
    
    @staticmethod
    def predownload_ocr_models():
        """Pre-download OCR models by running a dummy prediction."""
        try:
            # Use ImageProcessor's predownload method
            ImageProcessor.predownload_ocr_models()
        except Exception as e:
            print(f"Failed to pre-download OCR models: {e}") 