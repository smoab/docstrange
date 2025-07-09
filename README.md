# LLM Data Converter

Convert any document, text, or URL into LLM-ready data format.

## Installation

```bash
pip install llm-data-converter
```

## Quick Start

```python
from llm_converter import FileConverter
from litellm import completion

# Basic conversion
converter = FileConverter()
result = converter.convert("document.pdf").to_markdown()

# Pass the result to LLM
response = completion(
    model="openai/gpt-4o",
    messages=[{"content": f"Extract info from this document: \n{result}", "role": "user"}]
)
```

## Features

- **Multiple Input Formats**: PDF, DOCX, TXT, HTML, URLs, Excel files, and more
- **Multiple Output Formats**: Markdown, HTML, JSON, Plain Text
- **LLM Integration**: Seamless integration with LiteLLM and other LLM libraries
- **Local Processing**: Process documents locally without external dependencies
- **Layout Preservation**: Maintain document structure and formatting

## Usage Examples

### Convert PDF to Markdown

```python
from llm_converter import FileConverter

converter = FileConverter()
result = converter.convert("document.pdf").to_markdown()
print(result)
```

### Convert URL to HTML

```python
from llm_converter import FileConverter

converter = FileConverter()
result = converter.convert("https://example.com").to_html()
print(result)
```

### Convert Excel to JSON

```python
from llm_converter import FileConverter

converter = FileConverter()
result = converter.convert("data.xlsx").to_json()
print(result)
```

### Chain with LLM

```python
from llm_converter import FileConverter
from litellm import completion

converter = FileConverter()
document_content = converter.convert("report.pdf").to_markdown()

# Use with any LLM
response = completion(
    model="openai/gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that analyzes documents."},
        {"role": "user", "content": f"Summarize this document:\n\n{document_content}"}
    ]
)

print(response.choices[0].message.content)
```

## Supported Formats

### Input Formats
- **Documents**: PDF, DOCX, TXT
- **Web**: URLs, HTML files
- **Data**: Excel (XLSX, XLS), CSV
- **Images**: PNG, JPG, JPEG (with OCR capabilities)

### Output Formats
- **Markdown**: Clean, structured markdown
- **HTML**: Formatted HTML with styling
- **JSON**: Structured JSON data
- **Plain Text**: Simple text extraction

## Advanced Usage

### Custom Configuration

```python
from llm_converter import FileConverter

converter = FileConverter(
    preserve_layout=True,
    include_images=True,
    ocr_enabled=True
)

result = converter.convert("document.pdf").to_markdown()
```

### Batch Processing

```python
from llm_converter import FileConverter

converter = FileConverter()
files = ["doc1.pdf", "doc2.docx", "doc3.xlsx"]

results = []
for file in files:
    result = converter.convert(file).to_markdown()
    results.append(result)
```

## API Reference

### FileConverter

Main class for converting documents to LLM-ready formats.

#### Methods

- `convert(file_path: str) -> ConversionResult`: Convert a file to internal format
- `convert_url(url: str) -> ConversionResult`: Convert a URL to internal format
- `convert_text(text: str) -> ConversionResult`: Convert plain text to internal format

### ConversionResult

Result object with methods to export to different formats.

#### Methods

- `to_markdown() -> str`: Export as markdown
- `to_html() -> str`: Export as HTML
- `to_json() -> dict`: Export as JSON
- `to_text() -> str`: Export as plain text

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 