#!/usr/bin/env python3
"""
LLM integration example for llm-data-converter library.
"""

from llm_converter import FileConverter


def main():
    """Demonstrate LLM integration with the library."""
    
    # Initialize the converter
    converter = FileConverter()
    
    print("=== LLM Data Converter - LLM Integration Example ===\n")
    
    # Example: Convert document and use with LLM
    print("1. Converting document and preparing for LLM...")
    try:
        # Create a sample document
        with open("sample_document.txt", "w") as f:
            f.write("""
# Sample Business Report

## Executive Summary
This is a sample business report for demonstration purposes.

## Key Findings
- Revenue increased by 15% this quarter
- Customer satisfaction improved to 4.2/5
- New product launch was successful

## Recommendations
1. Continue current marketing strategy
2. Invest in customer support
3. Expand product line

## Financial Data
| Metric | Q1 | Q2 | Q3 | Q4 |
|--------|----|----|----|----|
| Revenue | $1M | $1.1M | $1.2M | $1.3M |
| Profit | $200K | $220K | $240K | $260K |
| Growth | 10% | 15% | 20% | 25% |
            """)
        
        # Convert the document
        result = converter.convert("sample_document.txt").to_markdown()
        print("✅ Document converted successfully!")
        
        # Prepare prompt for LLM
        prompt = f"""
Please analyze the following business report and provide insights:

{result}

Please provide:
1. A brief summary of the key points
2. The most important recommendation
3. Any potential concerns or risks
"""
        
        print("\n2. Prepared prompt for LLM:")
        print("=" * 50)
        print(prompt)
        print("=" * 50)
        
        # Note: In a real scenario, you would use this with an actual LLM
        print("\n3. LLM Integration (simulated):")
        print("To use with LiteLLM:")
        print("""
from litellm import completion

response = completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": prompt}]
)
print(response.choices[0].message.content)
        """)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example: Batch processing
    print("4. Batch processing example:")
    try:
        # Create multiple sample files
        files = []
        for i in range(3):
            filename = f"document_{i+1}.txt"
            with open(filename, "w") as f:
                f.write(f"This is document {i+1} for batch processing.\n\nIt contains sample content for testing.")
            files.append(filename)
        
        print(f"Created {len(files)} sample files for batch processing.")
        
        # Process all files
        results = []
        for file in files:
            result = converter.convert(file).to_markdown()
            results.append(result)
            print(f"✅ Processed {file}")
        
        print(f"\nSuccessfully processed {len(results)} files!")
        
        # Combine results for LLM
        combined_content = "\n\n---\n\n".join(results)
        combined_prompt = f"""
Please summarize the key points from these documents:

{combined_content}

Provide a brief overview of the main topics covered.
"""
        
        print("\n5. Combined prompt for LLM:")
        print("=" * 50)
        print(combined_prompt[:200] + "...")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 