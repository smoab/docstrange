#!/usr/bin/env python3
"""Example usage of the LLM Data Converter."""

from llm_converter import FileConverter

def main():
    # Example with local mode (default)
    print("=== Local Mode Example ===")
    converter = FileConverter()
    
    # You can test with any document, image, or URL
    # result = converter.convert("path/to/your/document.pdf")
    # print(result.to_markdown())
    
    # Test with simple text content
    test_content = """
    # Test Document
    
    This is a sample document with a table:
    
    | Name | Age | City |
    |------|-----|------|
    | John | 25  | NYC  |
    | Jane | 30  | LA   |
    | Bob  | 35  | SF   |
    
    And some regular text content.
    """
    
    result = converter.convert_text(test_content)
    
    print("Markdown output:")
    print(result.to_markdown())
    print("\n" + "="*50 + "\n")
    
    print("CSV output (tables only):")
    try:
        csv_output = result.to_csv()
        print(csv_output)
    except ValueError as e:
        print(f"CSV Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example with cloud mode (requires API key)
    print("=== Cloud Mode Example ===")
    try:
        # Cloud mode example - replace with your API key
        cloud_converter = FileConverter(
            cloud_mode=True, 
            api_key="<api-key>"  # Replace with actual key from https://app.nanonets.com/#/keys
        )
        
        # Uncomment to test with cloud mode:
        # result = cloud_converter.convert("path/to/your/document.pdf")
        # print(result.to_markdown())
        
        print("Cloud converter initialized successfully!")
        print("Replace '<api-key>' with your actual API key to test cloud mode.")
        
    except Exception as e:
        print(f"Cloud mode example (demo only): {e}")

if __name__ == "__main__":
    main()
