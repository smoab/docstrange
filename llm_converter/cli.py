"""Command-line interface for llm-data-converter."""

import argparse
import sys
import os
import json
from pathlib import Path
from typing import List

from .converter import FileConverter
from .exceptions import ConversionError, UnsupportedFormatError, FileNotFoundError
from . import __version__


def print_version():
    """Print version information."""
    print(f"llm-data-converter v{__version__}")
    print("Convert any document, text, or URL into LLM-ready data format")
    print("with advanced intelligent document processing capabilities.")


def print_supported_formats(converter: FileConverter):
    """Print supported formats in a nice format."""
    print("Supported input formats:")
    print()
    
    formats = converter.get_supported_formats()
    
    # Group formats by category
    categories = {
        "Documents": [f for f in formats if f in ['.pdf', '.docx', '.doc', '.txt', '.text']],
        "Data Files": [f for f in formats if f in ['.xlsx', '.xls', '.csv']],
        "Presentations": [f for f in formats if f in ['.ppt', '.pptx']],
        "Web": [f for f in formats if f == 'URLs'],
        "Images": [f for f in formats if f in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif']],
        "Web Files": [f for f in formats if f in ['.html', '.htm']]
    }
    
    for category, format_list in categories.items():
        if format_list:
            print(f"  {category}:")
            for fmt in format_list:
                print(f"    - {fmt}")
            print()


def process_single_input(converter: FileConverter, input_item: str, verbose: bool = False) -> dict:
    """Process a single input item and return result with metadata."""
    if verbose:
        print(f"Processing: {input_item}", file=sys.stderr)
    
    try:
        # Check if it's a URL
        if input_item.startswith(('http://', 'https://')):
            result = converter.convert_url(input_item)
            input_type = "URL"
        # Check if it's a file
        elif os.path.exists(input_item):
            result = converter.convert(input_item)
            input_type = "File"
        # Treat as text
        else:
            result = converter.convert_text(input_item)
            input_type = "Text"
        
        return {
            "success": True,
            "result": result,
            "input_type": input_type,
            "input_item": input_item
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "error": "File not found",
            "input_item": input_item
        }
    except UnsupportedFormatError:
        return {
            "success": False,
            "error": "Unsupported format",
            "input_item": input_item
        }
    except ConversionError as e:
        return {
            "success": False,
            "error": f"Conversion error: {e}",
            "input_item": input_item
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "input_item": input_item
        }


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Convert documents to LLM-ready formats with intelligent document processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a PDF to markdown (default)
  llm-converter document.pdf

  # Convert to different output formats
  llm-converter document.pdf --output html
  llm-converter document.pdf --output json
  llm-converter document.pdf --output text

  # Convert a URL
  llm-converter https://example.com --output html

  # Convert plain text
  llm-converter "Hello world" --output json

  # Convert multiple files
  llm-converter file1.pdf file2.docx --output markdown

  # Save output to file
  llm-converter document.pdf --output-file output.md

  # Enable intelligent document processing
  llm-converter image.png --ocr-enabled

  # List supported formats
  llm-converter --list-formats

  # Show version
  llm-converter --version
        """
    )
    
    parser.add_argument(
        "input",
        nargs="*",
        help="Input file(s), URL(s), or text to convert"
    )
    
    parser.add_argument(
        "--output", "-o",
        choices=["markdown", "html", "json", "text"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "--preserve-layout",
        action="store_true",
        default=True,
        help="Preserve document layout (default: True)"
    )
    
    parser.add_argument(
        "--include-images",
        action="store_true",
        help="Include images in output"
    )
    
    parser.add_argument(
        "--ocr-enabled",
        action="store_true",
        help="Enable intelligent document processing for images and PDFs"
    )
    
    parser.add_argument(
        "--output-file", "-f",
        help="Output file path (if not specified, prints to stdout)"
    )
    
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List supported input formats and exit"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Handle version flag
    if args.version:
        print_version()
        return 0
    
    # Handle list formats flag
    if args.list_formats:
        converter = FileConverter()
        print_supported_formats(converter)
        return 0
    
    # Check if input is provided
    if not args.input:
        parser.error("No input specified. Please provide file(s), URL(s), or text to convert.")
    
    # Initialize converter
    converter = FileConverter(
        preserve_layout=True,
        include_images=True,
        ocr_enabled=True
    )
    
    if args.verbose:
        print(f"Initialized converter with:")
        print(f"  - Preserve layout: True")
        print(f"  - Include images: True")
        print(f"  - Intelligent processing: True")
        print(f"  - Output format: {args.output}")
        print()
    
    # Process inputs
    results = []
    errors = []
    
    for i, input_item in enumerate(args.input, 1):
        if args.verbose and len(args.input) > 1:
            print(f"[{i}/{len(args.input)}] Processing: {input_item}", file=sys.stderr)
        
        result = process_single_input(converter, input_item, args.verbose)
        
        if result["success"]:
            results.append(result["result"])
            if not args.verbose:
                print(f"✅ Processed: {input_item}", file=sys.stderr)
        else:
            errors.append(result)
            print(f"❌ Failed: {input_item} - {result['error']}", file=sys.stderr)
    
    # Check if we have any successful results
    if not results:
        print("❌ No files were successfully processed.", file=sys.stderr)
        if errors:
            print("Errors encountered:", file=sys.stderr)
            for error in errors:
                print(f"  - {error['input_item']}: {error['error']}", file=sys.stderr)
        return 1
    
    # Generate output
    if len(results) == 1:
        # Single result
        result = results[0]
        if args.output == "markdown":
            output_content = result.to_markdown()
        elif args.output == "html":
            output_content = result.to_html()
        elif args.output == "json":
            output_content = json.dumps(result.to_json(), indent=2)
        else:  # text
            output_content = result.to_text()
    else:
        # Multiple results - combine them
        if args.output == "markdown":
            output_content = "\n\n---\n\n".join(r.to_markdown() for r in results)
        elif args.output == "html":
            output_content = "\n\n<hr>\n\n".join(r.to_html() for r in results)
        elif args.output == "json":
            combined_json = {
                "results": [r.to_json() for r in results],
                "count": len(results),
                "errors": [{"input": e["input_item"], "error": e["error"]} for e in errors] if errors else []
            }
            output_content = json.dumps(combined_json, indent=2)
        else:  # text
            output_content = "\n\n---\n\n".join(r.to_text() for r in results)
    
    # Write output
    if args.output_file:
        try:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"✅ Output written to: {args.output_file}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Failed to write output file: {e}", file=sys.stderr)
            return 1
    else:
        print(output_content)
    
    # Summary
    if args.verbose or len(args.input) > 1:
        print(f"\nSummary: {len(results)} successful, {len(errors)} failed", file=sys.stderr)
    
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main()) 