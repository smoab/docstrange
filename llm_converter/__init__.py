"""
LLM Data Converter - Convert any document, text, or URL into LLM-ready data format.
"""

from .converter import FileConverter
from .result import ConversionResult
from .exceptions import ConversionError, UnsupportedFormatError

__version__ = "0.1.0"
__all__ = ["FileConverter", "ConversionResult", "ConversionError", "UnsupportedFormatError"] 