#!/usr/bin/env python3
"""
Simple test script to convert a PDF document to markdown with OCR support.
"""

from llm_converter import FileConverter

def main():
    
    file_path = "sample_documents/sample.png"
    
    converter = FileConverter()
    
    result = converter.convert(file_path).to_markdown()
    
    print("📝=============================== Markdown Output:===============================")
    print(result)

if __name__ == "__main__":
    main() 