#!/usr/bin/env python3
from document_extractor import DocumentExtractor


file_path = "sample_documents/invoice.pdf"

extractor = DocumentExtractor(
    # api_key="<your-api-key>"  # Optional: for unlimited access
    cpu=True
)


# # # Standard conversions
# # result = extractor.extract(file_path).extract_csv()
# # print("📝=============================== CSV Output:===============================")
# # print(result)

# # result = extractor.extract(file_path).extract_html()
# # print("📝=============================== HTML Output:===============================")
# # print(result)

print("📝=============================== JSON Output:===============================")
result = extractor.extract(file_path).extract_data()
print(result)



# Intelligent field extraction examples (works with both cloud and local modes)
print("\n📝=============================== Intelligent Field Extraction:===============================")

# Example 1: Extract specific fields
result = extractor.extract(file_path)
try:
    specific_fields = result.extract_data(specified_fields=[
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
    
    structured_data = result.extract_data(json_schema=schema)
    print("JSON schema extraction:")
    print(structured_data)
except Exception as e:
    print(f"Schema extraction failed: {e}")
