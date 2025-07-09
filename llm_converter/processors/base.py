"""Base processor class for document conversion."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..result import ConversionResult
from llm_converter.config import InternalConfig


class BaseProcessor(ABC):
    """Base class for all document processors."""
    
    def __init__(self, preserve_layout: bool = True, include_images: bool = False, ocr_enabled: bool = False, use_markdownify: bool = InternalConfig.use_markdownify):
        """Initialize the processor.
        
        Args:
            preserve_layout: Whether to preserve document layout
            include_images: Whether to include images in output
            ocr_enabled: Whether to enable OCR for image processing
            use_markdownify: Whether to use markdownify for HTML->Markdown conversion
        """
        self.preserve_layout = preserve_layout
        self.include_images = include_images
        self.ocr_enabled = ocr_enabled
        self.use_markdownify = use_markdownify
    
    @abstractmethod
    def can_process(self, file_path: str) -> bool:
        """Check if this processor can handle the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this processor can handle the file
        """
        pass
    
    @abstractmethod
    def process(self, file_path: str) -> ConversionResult:
        """Process the file and return a conversion result.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            ConversionResult containing the processed content
            
        Raises:
            ConversionError: If processing fails
        """
        pass
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get basic metadata about the file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file metadata
        """
        import os
        import stat
        
        metadata = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),
            "file_extension": os.path.splitext(file_path)[1].lower(),
            "processor": self.__class__.__name__,
            "preserve_layout": self.preserve_layout,
            "include_images": self.include_images,
            "ocr_enabled": self.ocr_enabled
        }
        
        # Get file stats
        try:
            stat_info = os.stat(file_path)
            metadata.update({
                "created_time": stat_info.st_ctime,
                "modified_time": stat_info.st_mtime,
                "access_time": stat_info.st_atime
            })
        except OSError:
            pass
        
        return metadata 