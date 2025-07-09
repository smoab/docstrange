"""Main converter class for handling document conversion."""

import os
import logging
from typing import List, Optional

from .processors import (
    PDFProcessor,
    DOCXProcessor,
    TXTProcessor,
    ExcelProcessor,
    URLProcessor,
    HTMLProcessor,
    PPTXProcessor,
    ImageProcessor
)
from .result import ConversionResult
from .exceptions import ConversionError, UnsupportedFormatError, FileNotFoundError

# Configure logging
logger = logging.getLogger(__name__)


class FileConverter:
    """Main class for converting documents to LLM-ready formats."""
    
    def __init__(
        self,
        preserve_layout: bool = True,
        include_images: bool = True,
        ocr_enabled: bool = True
    ):
        """Initialize the file converter.
        
        Args:
            preserve_layout: Whether to preserve document layout
            include_images: Whether to include images in output
            ocr_enabled: Whether to enable OCR for image and PDF processing
        """
        self.preserve_layout = preserve_layout
        self.include_images = include_images
        # Default to True if not explicitly set
        if ocr_enabled is None:
            self.ocr_enabled = True
        else:
            self.ocr_enabled = ocr_enabled
        
        # Initialize processors in order of preference
        self.processors = [
            PDFProcessor(preserve_layout=preserve_layout, include_images=include_images, ocr_enabled=self.ocr_enabled),
            DOCXProcessor(preserve_layout=preserve_layout, include_images=include_images),
            TXTProcessor(preserve_layout=preserve_layout, include_images=include_images),
            ExcelProcessor(preserve_layout=preserve_layout, include_images=include_images),
            HTMLProcessor(preserve_layout=preserve_layout, include_images=include_images),
            PPTXProcessor(preserve_layout=preserve_layout, include_images=include_images),
            ImageProcessor(preserve_layout=preserve_layout, include_images=include_images, ocr_enabled=self.ocr_enabled),
            URLProcessor(preserve_layout=preserve_layout, include_images=include_images)
        ]
    
    def convert(self, file_path: str) -> ConversionResult:
        """Convert a file to internal format.
        
        Args:
            file_path: Path to the file to convert
            
        Returns:
            ConversionResult containing the processed content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            UnsupportedFormatError: If the format is not supported
            ConversionError: If conversion fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Find the appropriate processor
        processor = self._get_processor(file_path)
        if not processor:
            raise UnsupportedFormatError(f"No processor found for file: {file_path}")
        
        logger.info(f"Using processor {processor.__class__.__name__} for {file_path}")
        
        # Process the file
        return processor.process(file_path)
    
    def convert_url(self, url: str) -> ConversionResult:
        """Convert a URL to internal format.
        
        Args:
            url: URL to convert
            
        Returns:
            ConversionResult containing the processed content
            
        Raises:
            ConversionError: If conversion fails
        """
        # Find the URL processor
        url_processor = None
        for processor in self.processors:
            if isinstance(processor, URLProcessor):
                url_processor = processor
                break
        
        if not url_processor:
            raise ConversionError("URL processor not available")
        
        logger.info(f"Converting URL: {url}")
        return url_processor.process(url)
    
    def convert_text(self, text: str) -> ConversionResult:
        """Convert plain text to internal format.
        
        Args:
            text: Plain text to convert
            
        Returns:
            ConversionResult containing the processed content
        """
        metadata = {
            "content_type": "text",
            "processor": "TextConverter",
            "preserve_layout": self.preserve_layout
        }
        
        return ConversionResult(text, metadata)
    
    def _get_processor(self, file_path: str):
        """Get the appropriate processor for the file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Processor that can handle the file, or None if none found
        """
        for processor in self.processors:
            if processor.can_process(file_path):
                return processor
        return None
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats.
        
        Returns:
            List of supported file extensions
        """
        formats = []
        for processor in self.processors:
            if hasattr(processor, 'can_process'):
                # This is a simplified way to get formats
                # In a real implementation, you might want to store this info
                if isinstance(processor, PDFProcessor):
                    formats.extend(['.pdf'])
                elif isinstance(processor, DOCXProcessor):
                    formats.extend(['.docx', '.doc'])
                elif isinstance(processor, TXTProcessor):
                    formats.extend(['.txt', '.text'])
                elif isinstance(processor, ExcelProcessor):
                    formats.extend(['.xlsx', '.xls', '.csv'])
                elif isinstance(processor, HTMLProcessor):
                    formats.extend(['.html', '.htm'])
                elif isinstance(processor, PPTXProcessor):
                    formats.extend(['.ppt', '.pptx'])
                elif isinstance(processor, ImageProcessor):
                    formats.extend(['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'])
                elif isinstance(processor, URLProcessor):
                    formats.append('URLs')
        
        return formats 