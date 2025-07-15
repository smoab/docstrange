# LLM Data Converter v2.0.0

Convert any document, text, or URL into LLM-ready data format with advanced neural OCR capabilities powered by state-of-the-art pre-trained models.

## Installation

```bash
pip install llm-data-converter
```

**Requirements:**
- Python 3.8 or higher

### System Dependencies for Neural OCR

For neural OCR functionality to work properly, you may need to install additional system dependencies:

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

**Note:** The package will automatically download and cache neural models on first use.

## Quick Start

```python
from llm_converter import FileConverter

# Basic conversion with neural OCR
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
- **Neural OCR**: Advanced document understanding powered by state-of-the-art pre-trained models:
  - **Layout Detection**: Neural models for document structure understanding
  - **Text Recognition**: High-accuracy OCR with confidence scoring
  - **Table Structure**: Intelligent table detection and parsing with proper markdown output
  - **Automatic Model Download**: Models are automatically downloaded and cached

## Neural Document Processing

Version 2.0.0 introduces advanced neural document processing capabilities:

### Neural OCR (Default)
Uses state-of-the-art pre-trained models for superior accuracy:
- **Layout Detection**: Advanced neural models for document structure understanding
- **Text Recognition**: High-accuracy OCR with confidence scoring
- **Table Structure**: Intelligent table detection and parsing with proper markdown output
- **Automatic Model Download**: Models are automatically downloaded on first use
- **Document Understanding**: Comprehensive document analysis beyond simple OCR

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
result = converter.convert_url("https://example.com").to_html()
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
- **Images**: PNG, JPG, JPEG (with neural OCR capabilities)

### Output Formats
- **Markdown**: Clean, structured markdown with proper table formatting
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
print(result)
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

### Testing Neural OCR

```python
# Test the neural OCR capabilities
from llm_converter.pipeline.neural_document_processor import NeuralDocumentProcessor

# Initialize neural document processor
processor = NeuralDocumentProcessor()

# Extract text with layout awareness
text = processor.extract_text_with_layout("sample.png")
print(text)
```

## API Reference

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Third-Party Dependencies

This project uses several third-party libraries:

- **EasyOCR** - Apache 2.0 License (https://github.com/JaidedAI/EasyOCR)
- **PyTorch** - BSD 3-Clause License (https://pytorch.org/)
- **Transformers** - Apache 2.0 License (https://github.com/huggingface/transformers)
- **Pillow** - HPND License (https://python-pillow.org/)
- **python-docx** - MIT License (https://github.com/python-openxml/python-docx)
- **pandas** - BSD 3-Clause License (https://pandas.pydata.org/)
- **numpy** - BSD 3-Clause License (https://numpy.org/)
- **pdf2image** - MIT License (https://github.com/Belval/pdf2image)
- **markdownify** - MIT License (https://github.com/matthewwithanm/markdownify)

All dependencies are used in accordance with their respective licenses. 