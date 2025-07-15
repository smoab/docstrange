#!/usr/bin/env python3
import logging
from llm_converter import FileConverter
from llm_converter.config import InternalConfig

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

print("=== OCR Provider Debug ===")
print(f"Default OCR provider: {InternalConfig.ocr_provider}")

file_path = "sample_documents/sample.png"

print(f"\n=== Testing with file: {file_path} ===")

converter = FileConverter()

# Test the conversion
result = converter.convert(file_path).to_markdown()

print("\n📝=============================== Markdown Output:===============================")
print(result) 