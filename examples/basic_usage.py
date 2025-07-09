#!/usr/bin/env python3
"""
Basic usage example for llm-data-converter library.
"""

from llm_converter import FileConverter


def main():
    """Demonstrate basic usage of the library."""
    
    # Initialize the converter
    converter = FileConverter()
    
    print("=== LLM Data Converter - Basic Usage Example ===\n")
    
    # Example 1: Convert a text file
    print("1. Converting text file...")
    try:
        # Create a sample text file
        with open("sample.txt", "w") as f:
            f.write("This is a sample text file.\n\nIt contains multiple lines.\n\nThis is for testing the converter.")
        
        result = converter.convert("sample.txt").to_markdown()
        print("✅ Text file converted successfully!")
        print(f"Content: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Convert a URL
    print("2. Converting URL...")
    try:
        result = converter.convert_url("https://httpbin.org/html").to_markdown()
        print("✅ URL converted successfully!")
        print(f"Content: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Convert plain text
    print("3. Converting plain text...")
    try:
        text = "This is some plain text that we want to convert."
        result = converter.convert_text(text).to_markdown()
        print("✅ Plain text converted successfully!")
        print(f"Content: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Show supported formats
    print("4. Supported formats:")
    formats = converter.get_supported_formats()
    for fmt in formats:
        print(f"   - {fmt}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 5: Different output formats
    print("5. Different output formats:")
    try:
        text = "Sample text for format demonstration."
        result = converter.convert_text(text)
        
        print("   Markdown:")
        print(f"   {result.to_markdown()}")
        
        print("\n   HTML:")
        print(f"   {result.to_html()[:200]}...")
        
        print("\n   JSON:")
        print(f"   {result.to_json()}")
        
        print("\n   Plain text:")
        print(f"   {result.to_text()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 