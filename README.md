# Document Data Extractor

[![PyPI version](https://badge.fury.io/py/document-data-extractor.svg?v=2)](https://badge.fury.io/py/document-data-extractor)
<!-- [![Downloads](https://pepy.tech/badge/document-data-extractor)](https://pepy.tech/project/document-data-extractor) -->
[![Python](https://img.shields.io/pypi/pyversions/document-data-extractor.svg)](https://pypi.org/project/document-data-extractor/)
[![GitHub stars](https://img.shields.io/github/stars/NanoNets/document-data-extractor?style=social)](https://github.com/NanoNets/document-data-extractor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Try Cloud Mode for Free!**  
> Extract documents data instantly with our cloud API - no setup required.  
> For unlimited processing, [get your free API key](https://app.nanonets.com/#/keys).

Transform any document, image, or URL into LLM-ready formats (Markdown, JSON, CSV, HTML) with intelligent content extraction and advanced OCR.

## Key Features

- **Cloud Processing (Default)**: Instant conversion with Nanonets API - no local setup needed
- **Local Processing**: CPU/GPU options for complete privacy and control
- **Universal Input**: PDFs, Word docs, Excel, PowerPoint, images, URLs, and raw text
- **Smart Output**: Markdown, JSON, CSV, HTML, and plain text formats
- **LLM-Optimized**: Clean, structured output perfect for AI processing
- **Intelligent Extraction**: Extract specific fields or structured data using AI
- **Advanced OCR**: Multiple OCR engines with automatic fallback
- **Table Processing**: Accurate table extraction and formatting
- **Image Handling**: Extract text from images and visual content
- **URL Processing**: Direct conversion from web pages

## Installation

```bash
pip install document-data-extractor
```

## Quick Start

### Basic Usage (Cloud Mode - Default)

```python
from document_extractor import DocumentExtractor

# Default cloud mode - no setup required
extractor = DocumentExtractor()

# Extract data from any document
result = extractor.extract("document.pdf")

# Get different output formats
markdown = result.extract_markdown()
json_data = result.extract_data()
html = result.extract_html()
csv_tables = result.extract_csv()

# Extract specific fields
extracted_fields = result.extract_data(specified_fields=[
    "title", "author", "date", "summary", "key_points"
])

# Extract using JSON schema
schema = {
    "title": "string",
    "author": "string", 
    "date": "string",
    "summary": "string",
    "key_points": ["string"],
    "metadata": {
        "page_count": "number",
        "language": "string"
    }
}
structured_data = result.extract_data(json_schema=schema)
```

### With API Key (Unlimited Access)

```python
# Get your free API key from https://app.nanonets.com/#/keys
extractor = DocumentExtractor(api_key="your_api_key_here")
result = extractor.extract("document.pdf")
```

### Local Processing

```python
# Force local CPU processing
extractor = DocumentExtractor(cpu=True)

# Force local GPU processing (requires CUDA)
extractor = DocumentExtractor(gpu=True)
```

## Output Formats

- **Markdown**: Clean, LLM-friendly format with preserved structure
- **JSON**: Structured data with metadata and intelligent parsing
- **HTML**: Formatted output with styling and layout
- **CSV**: Extract tables and data in spreadsheet format
- **Text**: Plain text with smart formatting

## Examples

### Convert Multiple File Types

```python
from document_extractor import DocumentExtractor

extractor = DocumentExtractor()

# PDF document
pdf_result = extractor.extract("report.pdf")
print(pdf_result.extract_markdown())

# Word document  
docx_result = extractor.extract("document.docx")
print(docx_result.extract_data())

# Excel spreadsheet
excel_result = extractor.extract("data.xlsx")
print(excel_result.extract_csv())

# PowerPoint presentation
pptx_result = extractor.extract("slides.pptx")
print(pptx_result.extract_html())

# Image with text
image_result = extractor.extract("screenshot.png")
print(image_result.to_text())

# Web page
url_result = extractor.extract("https://example.com")
print(url_result.extract_markdown())
```

### Extract Tables to CSV

```python
# Extract all tables from a document
result = extractor.extract("financial_report.pdf")
csv_data = result.extract_csv(include_all_tables=True)
print(csv_data)
```

### Enhanced JSON Conversion

The library now uses intelligent document understanding for JSON conversion:

```python
from document_extractor import DocumentExtractor

extractor = DocumentExtractor()
result = extractor.extract("document.pdf")

# Enhanced JSON with Ollama (when available)
json_data = result.extract_data()
print(json_data["format"])  # "ollama_structured_json" or "structured_json"

# The enhanced conversion provides:
# - Better document structure understanding
# - Intelligent table parsing
# - Automatic metadata extraction  
# - Key information identification
# - Proper data type handling
```

**Requirements for enhanced JSON (if using cpu=True):**
- Install: `pip install 'document-data-extractor[local-llm]'`
- [Install Ollama](https://ollama.ai/) and run: `ollama serve`
- Pull a model: `ollama pull llama3.2`

*If Ollama is not available, the library automatically falls back to the standard JSON parser.*

### Extract Specific Fields & Structured Data

```python
# Extract specific fields from any document
result = extractor.extract("invoice.pdf")

# Method 1: Extract specific fields
extracted = result.extract_data(specified_fields=[
    "invoice_number", 
    "total_amount", 
    "vendor_name",
    "due_date"
])

# Method 2: Extract using JSON schema
schema = {
    "invoice_number": "string",
    "total_amount": "number", 
    "vendor_name": "string",
    "line_items": [{
        "description": "string",
        "amount": "number"
    }]
}

structured = result.extract_data(json_schema=schema)
```

**How it works:**
- Automatically uses cloud API when available
- Falls back to local Ollama for privacy-focused processing
- Same interface works for both cloud and local modes

**Cloud Mode Usage Examples:**

```python
from document_extractor import DocumentExtractor

# Default cloud mode (rate-limited without API key)
extractor = DocumentExtractor()

# With API key for unlimited access
extractor = DocumentExtractor(api_key="your_api_key_here")

# Extract specific fields from invoice
result = extractor.extract("invoice.pdf")

# Extract key invoice information
invoice_fields = result.extract_data(specified_fields=[
    "invoice_number",
    "total_amount", 
    "vendor_name",
    "due_date",
    "items_count"
])

print("Extracted Invoice Fields:")
print(invoice_fields)
# Output: {"extracted_fields": {"invoice_number": "INV-001", ...}, "format": "specified_fields"}

# Extract structured data using schema
invoice_schema = {
    "invoice_number": "string",
    "total_amount": "number",
    "vendor_name": "string",
    "billing_address": {
        "street": "string",
        "city": "string", 
        "zip_code": "string"
    },
    "line_items": [{
        "description": "string",
        "quantity": "number",
        "unit_price": "number",
        "total": "number"
    }],
    "taxes": {
        "tax_rate": "number",
        "tax_amount": "number"
    }
}

structured_invoice = result.extract_data(json_schema=invoice_schema)
print("Structured Invoice Data:")
print(structured_invoice)
# Output: {"structured_data": {...}, "schema": {...}, "format": "structured_json"}

# Extract from different document types
receipt = extractor.extract("receipt.jpg")
receipt_data = receipt.extract_data(specified_fields=[
    "merchant_name", "total_amount", "date", "payment_method"
])

contract = extractor.extract("contract.pdf") 
contract_schema = {
    "parties": [{
        "name": "string",
        "role": "string"
    }],
    "contract_value": "number",
    "start_date": "string",
    "end_date": "string",
    "key_terms": ["string"]
}
contract_data = contract.extract_data(json_schema=contract_schema)
```

**Local extraction requirements (if using cpu=True):**
- Install ollama package: `pip install 'document-data-extractor[local-llm]'`
- [Install Ollama](https://ollama.ai/) and run: `ollama serve`
- Pull a model: `ollama pull llama3.2`

### Chain with LLM

```python
# Perfect for LLM workflows
document_text = extractor.extract("research_paper.pdf").extract_markdown()

# Use with any LLM
response = your_llm_client.chat(
    messages=[{
        "role": "user", 
        "content": f"Summarize this research paper:\n\n{document_text}"
    }]
)
```

## Command Line Interface

```bash
# Basic conversion (cloud mode default)
document-data-extractor document.pdf

# With API key for unlimited access
document-data-extractor document.pdf --api-key YOUR_API_KEY

# Local processing modes
document-data-extractor document.pdf --cpu-mode
document-data-extractor document.pdf --gpu-mode

# Different output formats
document-data-extractor document.pdf --output json
document-data-extractor document.pdf --output html
document-data-extractor document.pdf --output csv

# Extract specific fields
document-data-extractor invoice.pdf --output json --extract-fields invoice_number total_amount

# Extract with JSON schema
document-data-extractor document.pdf --output json --json-schema schema.json

# Multiple files
document-data-extractor *.pdf --output markdown

# Save to file
document-data-extractor document.pdf --output-file result.md

# Comprehensive field extraction examples
document-data-extractor invoice.pdf --output json --extract-fields invoice_number vendor_name total_amount due_date line_items

# Extract from different document types with specific fields
document-data-extractor receipt.jpg --output json --extract-fields merchant_name total_amount date payment_method

document-data-extractor contract.pdf --output json --extract-fields parties contract_value start_date end_date

# Using JSON schema files for structured extraction
document-data-extractor invoice.pdf --output json --json-schema invoice_schema.json
document-data-extractor contract.pdf --output json --json-schema contract_schema.json

# Combine with API key for unlimited access
document-data-extractor document.pdf --api-key YOUR_API_KEY --output json --extract-fields title author date summary

# Force local processing with field extraction (requires Ollama)
document-data-extractor document.pdf --cpu-mode --output json --extract-fields key_points conclusions recommendations
```

**Example schema.json file:**
```json
{
  "invoice_number": "string",
  "total_amount": "number",
  "vendor_name": "string",
  "billing_address": {
    "street": "string",
    "city": "string",
    "zip_code": "string"
  },
  "line_items": [{
    "description": "string",
    "quantity": "number",
    "unit_price": "number"
  }]
}
```

## API Reference for library

### DocumentExtractor

```python
DocumentExtractor(
    preserve_layout: bool = True,      # Preserve document structure
    include_images: bool = True,       # Include image content
    ocr_enabled: bool = True,         # Enable OCR processing
    api_key: str = None,              # API key for unlimited cloud access
    model: str = None,                # Model for cloud processing ("gemini", "openapi")
    cpu: bool = False,     # Force local CPU processing
    gpu: bool = False      # Force local GPU processing
)
```

### ConversionResult Methods

```python
result.extract_markdown() -> str                    # Clean markdown output
result.extract_data(                              # Structured JSON
    specified_fields: List[str] = None,       # Extract specific fields
    json_schema: Dict = None                  # Extract with schema
) -> Dict
result.extract_html() -> str                      # Formatted HTML
result.extract_csv() -> str                       # CSV format for tables
result.to_text() -> str                      # Plain text
```

## Advanced Configuration

### Custom OCR Settings

```python
extractor = DocumentExtractor(
    cpu=True,        # Use local processing
    ocr_enabled=True,          # Enable OCR
    preserve_layout=True,      # Maintain structure
    include_images=True        # Process images
)
```

### Environment Variables

```bash
export NANONETS_API_KEY="your_api_key"
# Now all conversions use your API key automatically
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Email**: support@nanonets.com  
- **Issues**: [GitHub Issues](https://github.com/NanoNets/document-data-extractor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/NanoNets/document-data-extractor/discussions)

---

**Star this repo** if you find it helpful! Your support helps us improve the library. 