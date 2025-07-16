"""
LLM Data Converter - Convert any document, text, or URL into LLM-ready data format.
"""

from .converter import FileConverter
from .result import ConversionResult
from .exceptions import ConversionError, UnsupportedFormatError
from .config import InternalConfig

__version__ = "2.0.7"
__all__ = ["FileConverter", "ConversionResult", "ConversionError", "UnsupportedFormatError", "InternalConfig"] 