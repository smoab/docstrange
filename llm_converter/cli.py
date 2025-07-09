"""Command-line interface for llm-data-converter."""

import argparse
import sys
import os
from pathlib import Path

from .converter import FileConverter
from .exceptions import ConversionError, UnsupportedFormatError, FileNotFoundError


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Convert documents to LLM-ready formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a PDF to markdown
  llm-converter document.pdf --output markdown

  # Convert a URL to HTML
  llm-converter https://example.com --output html

  # Convert text to JSON
  llm-converter "Hello world" --output json

  # Convert multiple files
  llm-converter file1.pdf file2.docx --output markdown
        """
    )
    
    parser.add_argument(
        "input",
        nargs="+",
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
        help="Enable OCR for image processing"
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
    
    args = parser.parse_args()
    
    # Initialize converter
    converter = FileConverter(
        preserve_layout=args.preserve_layout,
        include_images=args.include_images,
        ocr_enabled=args.ocr_enabled
    )
    
    # List supported formats
    if args.list_formats:
        print("Supported input formats:")
        formats = converter.get_supported_formats()
        for fmt in formats:
            print(f"  - {fmt}")
        return 0
    
    # Process inputs
    results = []
    
    for input_item in args.input:
        try:
            # Check if it's a URL
            if input_item.startswith(('http://', 'https://')):
                result = converter.convert_url(input_item)
            # Check if it's a file
            elif os.path.exists(input_item):
                result = converter.convert(input_item)
            # Treat as text
            else:
                result = converter.convert_text(input_item)
            
            results.append(result)
            print(f"✅ Processed: {input_item}", file=sys.stderr)
            
        except FileNotFoundError:
            print(f"❌ File not found: {input_item}", file=sys.stderr)
            return 1
        except UnsupportedFormatError:
            print(f"❌ Unsupported format: {input_item}", file=sys.stderr)
            return 1
        except ConversionError as e:
            print(f"❌ Conversion error for {input_item}: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"❌ Unexpected error for {input_item}: {e}", file=sys.stderr)
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
            import json
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
            import json
            combined_json = {
                "results": [r.to_json() for r in results],
                "count": len(results)
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
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 