"""PDF file processor."""

import os
import logging
from typing import Dict, Any

from .base import BaseProcessor
from ..result import ConversionResult
from ..exceptions import ConversionError, FileNotFoundError

# Configure logging
logger = logging.getLogger(__name__)


class PDFProcessor(BaseProcessor):
    """Processor for PDF files using PyMuPDF with PyPDF2 fallback."""
    
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
        
        # Try PyMuPDF first (better text extraction)
        try:
            return self._process_with_pymupdf(file_path)
        except ImportError:
            logger.warning("PyMuPDF not available, falling back to PyPDF2")
            return self._process_with_pypdf2(file_path)
        except Exception as e:
            logger.warning(f"PyMuPDF failed: {e}, falling back to PyPDF2")
            return self._process_with_pypdf2(file_path)
    
    def _process_with_pymupdf(self, file_path: str) -> ConversionResult:
        """Process PDF using PyMuPDF for better text extraction."""
        try:
            import fitz  # PyMuPDF
            
            logger.info(f"Opening PDF with PyMuPDF: {file_path}")
            doc = fitz.open(file_path)
            logger.info(f"PDF opened successfully. Pages: {len(doc)}")
            
            content_parts = []
            page_count = len(doc)
            
            for page_num in range(page_count):
                logger.info(f"Processing page {page_num + 1}")
                page = doc.load_page(page_num)
                text = page.get_text()
                logger.info(f"Page {page_num + 1} text length: {len(text)}")
                
                if text.strip():
                    if self.preserve_layout:
                        content_parts.append(f"\n## Page {page_num + 1}\n")
                    content_parts.append(text)
            
            logger.info("Closing PDF document")
            doc.close()
            logger.info("PDF document closed successfully")
            
            content = "\n\n".join(content_parts)
            logger.info(f"Generated content length: {len(content)}")
            
            metadata = self.get_metadata(file_path)
            metadata.update({
                "page_count": page_count,
                "converter": "pymupdf"
            })
            
            # Clean up the content
            content = self._clean_content(content)
            
            return ConversionResult(content, metadata)
            
        except ImportError:
            raise ImportError("PyMuPDF is required for enhanced PDF processing. Install it with: pip install PyMuPDF")
        except Exception as e:
            logger.error(f"PyMuPDF conversion failed: {e}")
            raise ConversionError(f"PyMuPDF PDF conversion failed: {str(e)}")
    
    def _process_with_pypdf2(self, file_path: str) -> ConversionResult:
        """Process PDF using PyPDF2 as fallback."""
        try:
            import PyPDF2
            
            content_parts = []
            metadata = self.get_metadata(file_path)
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata.update({
                    "page_count": len(pdf_reader.pages),
                    "pdf_version": pdf_reader.metadata.get('/PDFVersion', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    "converter": "pypdf2"
                })
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            # Add page header
                            if self.preserve_layout:
                                content_parts.append(f"\n## Page {page_num}\n")
                            content_parts.append(page_text)
                    except Exception as e:
                        # If text extraction fails, add a note
                        content_parts.append(f"\n## Page {page_num}\n[Text extraction failed: {str(e)}]\n")
            
            content = '\n'.join(content_parts)
            
            # Clean up the content
            content = self._clean_content(content)
            
            return ConversionResult(content, metadata)
            
        except ImportError:
            raise ConversionError("PyPDF2 is required for PDF processing. Install it with: pip install PyPDF2")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, ConversionError)):
                raise
            raise ConversionError(f"Failed to process PDF file {file_path}: {str(e)}")
    
    def _clean_content(self, content: str) -> str:
        """Clean up the extracted PDF content.
        
        Args:
            content: Raw PDF text content
            
        Returns:
            Cleaned text content
        """
        # Remove excessive whitespace and normalize
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive whitespace
            line = ' '.join(line.split())
            if line.strip():
                cleaned_lines.append(line)
        
        # Join lines and add proper spacing
        content = '\n'.join(cleaned_lines)
        
        # Add spacing around headers
        content = content.replace('## Page', '\n## Page')
        
        return content.strip() 