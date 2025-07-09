"""Image file processor with OCR capabilities."""

import os
import logging
from typing import Dict, Any

from .base import BaseProcessor
from ..result import ConversionResult
from ..exceptions import ConversionError, FileNotFoundError

# Configure logging
logger = logging.getLogger(__name__)

# Global cache for PaddleOCR models
_paddle_ocr_cache = {}
_ppstructure_cache = None

os.environ['PADDLEOCR_HOME'] = os.path.expanduser('~/.paddlex/official_models')


class ImageProcessor(BaseProcessor):
    """Processor for image files (JPG, PNG, etc.) with OCR capabilities."""
    
    def can_process(self, file_path: str) -> bool:
        """Check if this processor can handle the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this processor can handle the file
        """
        if not os.path.exists(file_path):
            return False
        
        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        return ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif']
    
    def _check_models_downloaded(self):
        """Check if PaddleOCR models are already downloaded.
        
        Returns:
            True if models exist, False otherwise
        """
        model_dir = os.path.expanduser("~/.paddlex/official_models")
        return os.path.exists(model_dir)
    
    def _get_cached_ppstructure(self):
        """Get cached PPStructureV3 instance or create new one.
        
        Returns:
            PPStructureV3 instance
        """
        global _ppstructure_cache
        
        if _ppstructure_cache is None:
            try:
                from paddleocr import PPStructureV3
                
                # Check if models are already downloaded
                if self._check_models_downloaded():
                    logger.info("Using cached PPStructureV3 models...")
                else:
                    logger.info("Downloading PPStructureV3 models (this may take a moment on first run)...")
                
                _ppstructure_cache = PPStructureV3(
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False
                )
                logger.info("PPStructureV3 ready")
            except Exception as e:
                logger.error(f"Failed to initialize PPStructureV3: {e}")
                _ppstructure_cache = None
        
        return _ppstructure_cache
    
    def _get_cached_paddle_ocr(self):
        """Get cached PaddleOCR instance or create new one.
        
        Returns:
            PaddleOCR instance
        """
        global _paddle_ocr_cache
        
        cache_key = 'default'
        if cache_key not in _paddle_ocr_cache:
            try:
                from paddleocr import PaddleOCR
                
                # Check if models are already downloaded
                if self._check_models_downloaded():
                    logger.info("Using cached PaddleOCR models...")
                else:
                    logger.info("Downloading PaddleOCR models (this may take a moment on first run)...")
                
                _paddle_ocr_cache[cache_key] = PaddleOCR(use_angle_cls=True, lang='en')
                logger.info("PaddleOCR ready")
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                _paddle_ocr_cache[cache_key] = None
        
        return _paddle_ocr_cache[cache_key]
    
    def process(self, file_path: str) -> ConversionResult:
        """Process the image file and return a conversion result.
        
        Args:
            file_path: Path to the image file to process
            
        Returns:
            ConversionResult containing the processed content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ConversionError: If processing fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            from PIL import Image
            
            metadata = self.get_metadata(file_path)
            
            with Image.open(file_path) as img:
                # Extract image metadata
                image_info = {
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode,
                    "width": img.size[0],
                    "height": img.size[1]
                }
                
                # Create markdown content with image information
                content_parts = []
                content_parts.append(f"# Image: {os.path.basename(file_path)}")
                content_parts.append("")
                content_parts.append(f"**Format:** {image_info['format']}")
                content_parts.append(f"**Dimensions:** {image_info['width']} x {image_info['height']} pixels")
                content_parts.append(f"**Color Mode:** {image_info['mode']}")
                content_parts.append(f"**File Size:** {metadata.get('file_size', 'Unknown')} bytes")
                content_parts.append("")
                
                # Perform OCR if enabled
                if self.ocr_enabled:
                    ocr_text = self._perform_ocr(file_path)
                    if ocr_text:
                        content_parts.append("## Extracted Text (OCR)")
                        content_parts.append("")
                        content_parts.append(ocr_text)
                        content_parts.append("")
                        metadata.update({
                            "ocr_performed": True,
                            "ocr_text_length": len(ocr_text)
                        })
                    else:
                        content_parts.append("*OCR was performed but no text was detected in this image.*")
                        metadata.update({
                            "ocr_performed": True,
                            "ocr_text_length": 0
                        })
                else:
                    content_parts.append("*This image contains visual content that cannot be converted to text without OCR.*")
                    content_parts.append("*Enable OCR processing to extract text from this image.*")
                    metadata.update({
                        "ocr_performed": False
                    })
                
                content = "\n".join(content_parts)
                
                metadata.update({
                    "image_info": image_info,
                    "converter": "pillow"
                })
                
                return ConversionResult(content, metadata)
                
        except ImportError:
            raise ConversionError("Pillow is required for image processing. Install it with: pip install Pillow")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, ConversionError)):
                raise
            raise ConversionError(f"Failed to process image file {file_path}: {str(e)}")
    
    def _perform_ocr(self, file_path: str) -> str:
        """Perform OCR on the image using PaddleOCR with layout awareness (PPStructureV3), fallback to line-based OCR if needed.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Layout-aware markdown text from the image
        """
        try:
            # Try layout-aware OCR first
            try:
                pipeline = self._get_cached_ppstructure()
                results = pipeline.predict(input=file_path)
                markdown_parts = []
                for res in results:
                    md = res.markdown.get('markdown_texts', '')
                    if md:
                        # Debug: log HTML table structure
                        if '<table' in md:
                            logger.info(f"Found HTML table in markdown, length: {len(md)}")
                            # Find and log table structure
                            import re
                            table_match = re.search(r'<table[^>]*>(.*?)</table>', md, re.DOTALL)
                            if table_match:
                                logger.info(f"Table HTML structure found, length: {len(table_match.group(0))}")
                        
                        # Convert HTML tables to markdown tables
                        md = self._convert_html_tables_to_markdown(md)
                        # Clean up the markdown formatting
                        md = self._clean_markdown_formatting(md)
                        markdown_parts.append(md)
                if markdown_parts:
                    return "\n\n".join(markdown_parts)
            except Exception as e:
                import traceback
                logger.warning(f"PPStructureV3 layout-aware OCR failed: {e}\n{traceback.format_exc()}")
                # Fallback to line-based OCR below

            # Fallback: line-based OCR
            from paddleocr import PaddleOCR
            from PIL import Image
            import numpy as np
            ocr = self._get_cached_paddle_ocr()
            result = ocr.ocr(file_path)
            logger.info(f"Fallback OCR result type: {type(result)}")
            logger.info(f"Fallback OCR result length: {len(result) if result else 0}")
            if not result:
                logger.warning("Fallback OCR returned empty result")
                return ""
            with Image.open(file_path) as img:
                img_width, img_height = img.size
            text_blocks = self._extract_text_with_layout(result, img_width, img_height)
            logger.info(f"Fallback extracted {len(text_blocks)} text blocks")
            if not text_blocks:
                logger.warning("No text blocks extracted, falling back to simple extraction")
                return self._simple_text_extraction(result)
            markdown_content = self._convert_to_layout_markdown(text_blocks)
            logger.info(f"Total fallback extracted text length: {len(markdown_content)}")
            return markdown_content
        except ImportError as e:
            logger.warning(f"Import error: {e}. PaddleOCR not available. Install it with: pip install paddleocr")
            return ""
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            logger.exception("Full OCR error traceback:")
            try:
                return self._simple_text_extraction(result) if 'result' in locals() else ""
            except:
                return ""
    
    def _convert_html_tables_to_markdown(self, text):
        """Convert HTML tables to markdown tables with robust row handling for PaddleOCR output.
        
        Args:
            text: Text containing HTML tables
            
        Returns:
            Text with HTML tables converted to markdown
        """
        import re
        from bs4 import BeautifulSoup
        
        # Find HTML table patterns - handle PaddleOCR's specific div-wrapped table format
        table_pattern = r'<div[^>]*><html><body><table[^>]*>(.*?)</table></body></html></div>'
        
        def convert_table(match):
            table_html = match.group(1)
            try:
                # Parse the table HTML
                soup = BeautifulSoup(f'<table>{table_html}</table>', 'html.parser')
                table = soup.find('table')
                if not table:
                    return match.group(0)
                
                # Extract all rows
                rows = table.find_all('tr')
                if not rows:
                    return match.group(0)
                
                # Determine number of columns from the first row
                first_row = rows[0]
                first_cells = first_row.find_all(['td', 'th'])
                num_columns = len(first_cells)
                
                markdown_table = []
                
                for i, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    # Pad or truncate to match header columns
                    if len(row_data) < num_columns:
                        row_data += [''] * (num_columns - len(row_data))
                    elif len(row_data) > num_columns:
                        row_data = row_data[:num_columns]
                    markdown_row = '| ' + ' | '.join(row_data) + ' |'
                    markdown_table.append(markdown_row)
                    if i == 0:
                        separator = '|' + '|'.join(['---'] * num_columns) + '|'
                        markdown_table.append(separator)
                return '\n'.join(markdown_table)
            except Exception as e:
                logger.warning(f"Failed to convert HTML table to markdown: {e}")
                return match.group(0)
        
        # Replace HTML tables with markdown
        return re.sub(table_pattern, convert_table, text, flags=re.DOTALL)
    
    def _clean_markdown_formatting(self, text):
        """Clean up markdown formatting for better readability.
        
        Args:
            text: Raw markdown text
            
        Returns:
            Cleaned markdown text
        """
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Clean up header formatting
        text = re.sub(r'###\s+', '### ', text)
        text = re.sub(r'##\s+', '## ', text)
        text = re.sub(r'#\s+', '# ', text)
        
        # Remove HTML div wrappers
        text = re.sub(r'<div[^>]*>', '', text)
        text = re.sub(r'</div>', '', text)
        
        # Clean up table formatting
        text = re.sub(r'\|\s*\|\s*\|', '| | |', text)
        
        # Remove excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _simple_text_extraction(self, result):
        """Simple text extraction as fallback.
        
        Args:
            result: OCR result from PaddleOCR
            
        Returns:
            Simple text string
        """
        text_parts = []
        
        if isinstance(result, list):
            for page_result in result:
                if page_result:
                    for line in page_result:
                        if isinstance(line, list) and len(line) >= 2:
                            if len(line) >= 2 and isinstance(line[1], tuple) and len(line[1]) >= 1:
                                text = line[1][0]
                                if text and text.strip():
                                    text_parts.append(text.strip())
        
        return "\n".join(text_parts)
    
    def _extract_text_with_layout(self, result, img_width, img_height):
        """Extract text with layout information from OCR result.
        
        Args:
            result: OCR result from PaddleOCR
            img_width: Image width
            img_height: Image height
            
        Returns:
            List of text blocks with layout information
        """
        text_blocks = []
        
        if isinstance(result, list):
            for page_result in result:
                if page_result:
                    for line in page_result:
                        if isinstance(line, list) and len(line) >= 2:
                            # Format: [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, confidence)]
                            if len(line) >= 2 and isinstance(line[1], tuple) and len(line[1]) >= 1:
                                text = line[1][0]
                                confidence = line[1][1] if len(line[1]) > 1 else 0.0
                                
                                if text and text.strip():
                                    # Extract bounding box coordinates
                                    bbox = line[0] if line[0] else []
                                    if bbox and len(bbox) >= 4:
                                        # Calculate layout properties
                                        x_coords = [point[0] for point in bbox]
                                        y_coords = [point[1] for point in bbox]
                                        
                                        block_info = {
                                            'text': text.strip(),
                                            'confidence': confidence,
                                            'bbox': bbox,
                                            'x_min': min(x_coords),
                                            'x_max': max(x_coords),
                                            'y_min': min(y_coords),
                                            'y_max': max(y_coords),
                                            'width': max(x_coords) - min(x_coords),
                                            'height': max(y_coords) - min(y_coords),
                                            'center_x': (min(x_coords) + max(x_coords)) / 2,
                                            'center_y': (min(y_coords) + max(y_coords)) / 2,
                                            'relative_x': (min(x_coords) + max(x_coords)) / (2 * img_width),
                                            'relative_y': (min(y_coords) + max(y_coords)) / (2 * img_height)
                                        }
                                        text_blocks.append(block_info)
        
        return text_blocks
    
    def _convert_to_layout_markdown(self, text_blocks):
        """Convert text blocks to layout-aware markdown.
        
        Args:
            text_blocks: List of text blocks with layout information
            
        Returns:
            Layout-aware markdown string
        """
        if not text_blocks:
            return ""
        
        # Sort blocks by vertical position (top to bottom)
        text_blocks.sort(key=lambda x: x['y_min'])
        
        # Group blocks into lines and paragraphs
        lines = self._group_into_lines(text_blocks)
        paragraphs = self._group_into_paragraphs(lines)
        
        # Convert to markdown
        markdown_parts = []
        
        for paragraph in paragraphs:
            if not paragraph:
                continue
                
            # Analyze paragraph structure
            paragraph_type = self._analyze_paragraph_type(paragraph)
            
            if paragraph_type == 'header':
                # Use the first line as header
                header_text = paragraph[0]['text']
                markdown_parts.append(f"\n## {header_text}\n")
                
            elif paragraph_type == 'table':
                # Convert to markdown table
                table_markdown = self._convert_to_table(paragraph)
                markdown_parts.append(table_markdown)
                
            elif paragraph_type == 'list':
                # Convert to markdown list
                list_markdown = self._convert_to_list(paragraph)
                markdown_parts.append(list_markdown)
                
            else:
                # Regular paragraph
                paragraph_text = ' '.join([block['text'] for block in paragraph])
                markdown_parts.append(f"\n{paragraph_text}\n")
        
        return '\n'.join(markdown_parts)
    
    def _group_into_lines(self, text_blocks):
        """Group text blocks into lines based on vertical position.
        
        Args:
            text_blocks: List of text blocks
            
        Returns:
            List of lines (each line is a list of text blocks)
        """
        if not text_blocks:
            return []
        
        # Sort by y position
        text_blocks.sort(key=lambda x: x['y_min'])
        
        lines = []
        current_line = []
        line_threshold = 20  # pixels
        
        for block in text_blocks:
            if not current_line:
                current_line.append(block)
            else:
                # Check if this block is on the same line
                last_block = current_line[-1]
                y_diff = abs(block['y_min'] - last_block['y_min'])
                
                if y_diff <= line_threshold:
                    current_line.append(block)
                else:
                    # Start new line
                    if current_line:
                        lines.append(current_line)
                    current_line = [block]
        
        if current_line:
            lines.append(current_line)
        
        # Sort blocks within each line by x position
        for line in lines:
            line.sort(key=lambda x: x['x_min'])
        
        return lines
    
    def _group_into_paragraphs(self, lines):
        """Group lines into paragraphs based on spacing.
        
        Args:
            lines: List of lines
            
        Returns:
            List of paragraphs (each paragraph is a list of text blocks)
        """
        if not lines:
            return []
        
        paragraphs = []
        current_paragraph = []
        paragraph_threshold = 40  # pixels
        
        for line in lines:
            if not current_paragraph:
                current_paragraph.extend(line)
            else:
                # Check spacing between this line and the last line of current paragraph
                last_line_y = max(block['y_max'] for block in current_paragraph)
                current_line_y = min(block['y_min'] for block in line)
                spacing = current_line_y - last_line_y
                
                if spacing <= paragraph_threshold:
                    current_paragraph.extend(line)
                else:
                    # Start new paragraph
                    if current_paragraph:
                        paragraphs.append(current_paragraph)
                    current_paragraph = line
        
        if current_paragraph:
            paragraphs.append(current_paragraph)
        
        return paragraphs
    
    def _analyze_paragraph_type(self, paragraph):
        """Analyze paragraph type (header, table, list, regular).
        
        Args:
            paragraph: List of text blocks
            
        Returns:
            Paragraph type string
        """
        if not paragraph:
            return 'regular'
        
        # Check for header indicators
        first_text = paragraph[0]['text'].lower()
        if any(keyword in first_text for keyword in ['chapter', 'section', 'part', 'title', 'heading']):
            return 'header'
        
        # Check for table structure (multiple columns)
        if len(paragraph) > 1:
            # Check if blocks are arranged in columns
            x_positions = [block['center_x'] for block in paragraph]
            x_variance = np.var(x_positions) if len(x_positions) > 1 else 0
            
            # If x positions vary significantly, it might be a table
            if x_variance > 1000:  # threshold for table detection
                return 'table'
        
        # Check for list indicators
        first_block_text = paragraph[0]['text'].strip()
        if (first_block_text.startswith(('•', '-', '*', '1.', '2.', '3.', 'a.', 'b.', 'c.')) or
            any(keyword in first_block_text.lower() for keyword in ['item', 'list', 'bullet'])):
            return 'list'
        
        return 'regular'
    
    def _convert_to_table(self, paragraph):
        """Convert paragraph to markdown table.
        
        Args:
            paragraph: List of text blocks representing table data
            
        Returns:
            Markdown table string
        """
        if not paragraph:
            return ""
        
        # Group blocks by approximate x position (columns)
        columns = {}
        column_threshold = 100  # pixels
        
        for block in paragraph:
            x_pos = block['center_x']
            assigned = False
            
            for col_x in columns.keys():
                if abs(x_pos - col_x) <= column_threshold:
                    columns[col_x].append(block)
                    assigned = True
                    break
            
            if not assigned:
                columns[x_pos] = [block]
        
        # Sort columns by x position
        sorted_columns = sorted(columns.items())
        
        # Create table rows
        table_rows = []
        max_rows = max(len(col) for col in columns.values())
        
        for row_idx in range(max_rows):
            row_data = []
            for col_x, col_blocks in sorted_columns:
                if row_idx < len(col_blocks):
                    row_data.append(col_blocks[row_idx]['text'])
                else:
                    row_data.append('')
            table_rows.append(row_data)
        
        # Convert to markdown table
        if not table_rows:
            return ""
        
        markdown_table = []
        
        # Header row
        markdown_table.append('| ' + ' | '.join(table_rows[0]) + ' |')
        
        # Separator row
        markdown_table.append('|' + '|'.join(['---'] * len(table_rows[0])) + '|')
        
        # Data rows
        for row in table_rows[1:]:
            markdown_table.append('| ' + ' | '.join(row) + ' |')
        
        return '\n'.join(markdown_table)
    
    def _convert_to_list(self, paragraph):
        """Convert paragraph to markdown list.
        
        Args:
            paragraph: List of text blocks representing list items
            
        Returns:
            Markdown list string
        """
        if not paragraph:
            return ""
        
        list_items = []
        for block in paragraph:
            text = block['text'].strip()
            if text:
                # Remove list markers if present
                if text.startswith(('•', '-', '*', '1.', '2.', '3.', 'a.', 'b.', 'c.')):
                    text = text[1:].strip()
                list_items.append(f"- {text}")
        
        return '\n'.join(list_items)
    
    def _clean_content(self, content: str) -> str:
        """Clean up the image content.
        
        Args:
            content: Raw image content
            
        Returns:
            Cleaned text content
        """
        # For images, the content is already clean markdown
        return content.strip()

    @staticmethod
    def predownload_paddleocr_models(sample_image_path=None):
        """Pre-download all PaddleOCR models by running a dummy prediction once."""
        try:
            from paddleocr import PPStructureV3
            pipeline = PPStructureV3()
            if sample_image_path and os.path.exists(sample_image_path):
                pipeline.predict(input=sample_image_path)
            else:
                # Create a blank image if no sample provided
                from PIL import Image
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    img = Image.new('RGB', (100, 100), color='white')
                    img.save(tmp.name)
                    pipeline.predict(input=tmp.name)
                    os.unlink(tmp.name)
            print("PaddleOCR models pre-downloaded and cached.")
        except Exception as e:
            print(f"Failed to pre-download PaddleOCR models: {e}") 