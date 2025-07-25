#!/usr/bin/env python3
from llm_converter import FileConverter


file_path = "sample_documents/invoice.pdf"

# Default cloud mode - no setup required
# For unlimited access, get API key from https://app.nanonets.com/#/keys
converter = FileConverter(
    # api_key="<your-api-key>"  # Optional: for unlimited access
)

# For local processing, specify preference:
# converter = FileConverter(cpu_preference=True)   # Local CPU mode
# converter = FileConverter(gpu_preference=True)   # Local GPU mode

# # # Standard conversions
# # result = converter.convert(file_path).to_csv()
# # print("📝=============================== CSV Output:===============================")
# # print(result)

# # result = converter.convert(file_path).to_html()
# # print("📝=============================== HTML Output:===============================")
# # print(result)

print("📝=============================== JSON Output:===============================")
result = converter.convert(file_path).to_json()
print(result)

print("\n" + "="*50)
print("ENHANCED JSON CONVERSION")
print("="*50)

# Test enhanced JSON conversion
json_result = converter.convert(file_path).to_json()
print(f"JSON Format: {json_result.get('format', 'unknown')}")
print(f"Extractor: {json_result.get('extractor', 'standard')}")

if json_result.get('format') == 'ollama_structured_json':
    print("\n✅ Using Ollama-enhanced JSON conversion!")
    print("Benefits:")
    print("- Better document structure understanding")
    print("- Intelligent table parsing")
    print("- Automatic metadata extraction")
    print("- Key information identification")
    
    # Show some key sections
    if 'key_information' in json_result:
        print(f"\nExtracted {len(json_result['key_information'])} key information items")
    if 'document' in json_result and 'sections' in json_result['document']:
        sections = json_result['document']['sections']
        print(f"Organized into {len(sections)} main sections")
else:
    print("\n📋 Using standard JSON parser")
    if not converter.cloud_mode:
        print("💡 Tip: Install Ollama for enhanced JSON conversion!")
        print("   pip install 'llm-data-converter[local-llm]'")

# Intelligent field extraction examples (works with both cloud and local modes)
print("\n📝=============================== Intelligent Field Extraction:===============================")

# Example 1: Extract specific fields
result = converter.convert(file_path)
try:
    specific_fields = result.to_json(specified_fields=[
        "total_amount", 
        "date", 
        "vendor_name",
        "invoice_number"
    ])
    print("Specific fields extraction:")
    print(specific_fields)
except Exception as e:
    print(f"Field extraction failed: {e}")

print("\n" + "="*80 + "\n")

# Example 2: Extract using JSON schema
try:
    schema = {
        "invoice_number": "string",
        "total_amount": "number",
        "vendor_name": "string", 
        "items": [{
            "description": "string",
            "amount": "number"
        }]
    }
    
    structured_data = result.to_json(json_schema=schema)
    print("JSON schema extraction:")
    print(structured_data)
except Exception as e:
    print(f"Schema extraction failed: {e}")

result = converter.convert(file_path).to_text()

print("📝=============================== Markdown Output:===============================")
print(result)
