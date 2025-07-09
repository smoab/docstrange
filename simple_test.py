#!/usr/bin/env python3
"""
Simple test script to convert a document to markdown and print output.
"""

from llm_converter import FileConverter

def main():
    """Convert a document to markdown and print the output."""
    
    # Test with a sample file
    file_path = "sample_documents/sample.png"
    
    print("📄 Converting document to markdown...")
    print(f"File: {file_path}")
    print("-" * 50)
    
    try:
        # Initialize converter
        converter = FileConverter()
        
        # Convert file
        result = converter.convert(file_path)
        
        # Convert to markdown
        markdown = result.to_markdown()
        
        # Print the markdown output
        print("📝 Markdown Output:")
        print("=" * 50)
        print(markdown)
        print("=" * 50)
        
        # Print some basic info
        print(f"\n📊 Summary:")
        print(f"Content length: {len(result.content)} characters")
        print(f"Markdown length: {len(markdown)} characters")
        print(f"Metadata items: {len(result.metadata)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 