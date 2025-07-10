#!/usr/bin/env python3
"""
Test script for pytesseract OCR functionality.
"""

import os
import sys
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_converter.config import InternalConfig
from llm_converter.services.ocr_service import OCRServiceFactory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pytesseract_ocr():
    """Test pytesseract OCR functionality."""
    
    # Switch to pytesseract provider
    InternalConfig.ocr_provider = 'pytesseract'
    
    # Create OCR service
    try:
        ocr_service = OCRServiceFactory.create_service('pytesseract')
        logger.info("PytesseractOCRService created successfully")
    except Exception as e:
        logger.error(f"Failed to create PytesseractOCRService: {e}")
        return False
    
    # Test with a sample image if available
    test_image = "tests/test_files/sample_image.png"
    
    if os.path.exists(test_image):
        logger.info(f"Testing with image: {test_image}")
        
        # Test simple text extraction
        try:
            text = ocr_service.extract_text(test_image)
            logger.info(f"Simple text extraction result: {text[:200]}...")
        except Exception as e:
            logger.error(f"Simple text extraction failed: {e}")
        
        # Test layout-aware extraction
        try:
            layout_text = ocr_service.extract_text_with_layout(test_image)
            logger.info(f"Layout-aware extraction result: {layout_text[:200]}...")
        except Exception as e:
            logger.error(f"Layout-aware extraction failed: {e}")
    
    else:
        logger.warning(f"Test image not found: {test_image}")
        logger.info("Testing OCR service creation only")
    
    # Test available providers
    providers = OCRServiceFactory.get_available_providers()
    logger.info(f"Available OCR providers: {providers}")
    
    return True

def test_paddleocr_vs_pytesseract():
    """Compare PaddleOCR and pytesseract providers."""
    
    logger.info("Testing OCR provider comparison...")
    
    # Test PaddleOCR
    try:
        InternalConfig.ocr_provider = 'paddleocr'
        paddle_ocr = OCRServiceFactory.create_service('paddleocr')
        logger.info("PaddleOCR service created successfully")
    except Exception as e:
        logger.error(f"Failed to create PaddleOCR service: {e}")
    
    # Test pytesseract
    try:
        InternalConfig.ocr_provider = 'pytesseract'
        tesseract_ocr = OCRServiceFactory.create_service('pytesseract')
        logger.info("Pytesseract service created successfully")
    except Exception as e:
        logger.error(f"Failed to create Pytesseract service: {e}")
    
    # List available providers
    providers = OCRServiceFactory.get_available_providers()
    logger.info(f"Available OCR providers: {providers}")

if __name__ == "__main__":
    logger.info("Starting pytesseract OCR tests...")
    
    # Test pytesseract functionality
    success = test_pytesseract_ocr()
    
    # Test provider comparison
    test_paddleocr_vs_pytesseract()
    
    if success:
        logger.info("Pytesseract OCR tests completed successfully!")
    else:
        logger.error("Pytesseract OCR tests failed!")
        sys.exit(1) 