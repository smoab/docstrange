# LLM Data Converter v2.0.0

Convert any document, text, or URL into LLM-ready data format with advanced intelligent document processing capabilities powered by pre-trained models.

## Installation

```bash
pip install llm-data-converter
```

**Requirements:**
- Python 3.8 or higher

### System Dependencies for Intelligent Document Processing

For intelligent document processing functionality to work properly, you may need to install additional system dependencies:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y libgl1 libglib2.0-0 libgomp1
pip install setuptools
```

**macOS:**
```bash
# Usually not needed, but if you encounter OpenGL issues:
brew install mesa
```

**Note:** The package will automatically download and cache intelligent models on first use.

## Quick Start

```python
from llm_converter import FileConverter

# Basic conversion with intelligent document processing
converter = FileConverter()
result = converter.convert("document.pdf").to_markdown()
print(result)
```

## Features

- **Multiple Input Formats**: PDF, DOCX, TXT, HTML, URLs, Excel files, and more
- **Multiple Output Formats**: Markdown, HTML, JSON, Plain Text
- **LLM Integration**: Seamless integration with LiteLLM and other LLM libraries
- **Local Processing**: Process documents locally without external dependencies
- **Layout Preservation**: Maintain document structure and formatting
- **Intelligent Document Processing**: Advanced document understanding and conversion powered by pre-trained models:
  - **Layout Detection**: Intelligent models for document structure understanding
  - **Text Recognition**: High-accuracy text extraction with confidence scoring
  - **Table Structure**: Intelligent table detection and conversion to markdown format
  - **Automatic Model Download**: Models are automatically downloaded and cached

## Intelligent Document Processing

Version 2.0.0 introduces advanced intelligent document processing capabilities:

### Intelligent Document Processing (Default)
Uses pre-trained models for superior document conversion accuracy:
- **Layout Detection**: Advanced intelligent models for document structure understanding
- **Text Recognition**: High-accuracy text extraction with confidence scoring
- **Table Structure**: Intelligent table detection and conversion to markdown format
- **Automatic Model Download**: Models are automatically downloaded on first use
- **Document Understanding**: Comprehensive document analysis and conversion beyond simple text extraction

## Usage Examples

### Convert PDF to Markdown

```python
from llm_converter import FileConverter

converter = FileConverter()
result = converter.convert("document.pdf").to_markdown()
print(result)
```


### Convert Image to HTML

```python
from llm_converter import FileConverter

converter = FileConverter()
result = converter.convert("sample.png").to_html()
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
- **Images**: PNG, JPG, JPEG (with intelligent document processing capabilities)

### Output Formats
- **Markdown**: Clean, structured markdown with proper table formatting
- **HTML**: Formatted HTML with styling
- **JSON**: Structured JSON data
- **Plain Text**: Simple text extraction


## CLI usage

The `llm-converter` command-line tool provides easy access to all conversion features:

### Basic Usage

```bash
# Convert a PDF to markdown (default)
llm-converter document.pdf

# Convert to different output formats
llm-converter document.pdf --output html
llm-converter document.pdf --output json
llm-converter document.pdf --output text


```

### Advanced Options

```bash
# Save output to file
llm-converter document.pdf --output-file output.md

# For image input
llm-converter image.png 

# Convert multiple files at once
llm-converter file1.pdf file2.docx file3.xlsx --output markdown
```

### List Supported Formats

```bash
# See all supported input formats
llm-converter --list-formats
```

### Examples

```bash
# Convert PDF with intelligent document processing
llm-converter scanned_document.pdf --output markdown

# Convert image to HTML with layout preservation
llm-converter screenshot.png --output html

# Convert multiple documents to JSON
llm-converter report.pdf presentation.pptx data.xlsx --output json --output-file combined.json

# Convert URL content to markdown
llm-converter https://blog.example.com --output markdown --output-file blog_content.md
```

### Output Formats

- **markdown** (default): Clean, structured markdown
- **html**: Formatted HTML with styling
- **json**: Structured JSON data
- **text**: Plain text extraction


## API Reference for library

### FileConverter

Main class for converting documents to LLM-ready formats.

#### Methods

- `convert(file_path: str) -> ConversionResult`: Convert a file to internal format
- `convert_url(url: str) -> ConversionResult`: Convert a URL page contents to internal format
- `convert_text(text: str) -> ConversionResult`: Convert plain text to internal format

### ConversionResult

Result object with methods to export to different formats.

#### Methods

- `to_markdown() -> str`: Export as markdown
- `to_html() -> str`: Export as HTML
- `to_json() -> dict`: Export as JSON
- `to_text() -> str`: Export as plain text


## License

MIT License - see LICENSE file for details. 