"""OCR Service abstraction for different OCR providers."""

import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import threading
import re
import numpy as np

logger = logging.getLogger(__name__)

# Set PaddleOCR home directory
os.environ['PADDLEOCR_HOME'] = os.path.expanduser('~/.paddlex/official_models')


def check_opengl_availability():
    """Check if OpenGL is available and provide helpful error message if not."""
    try:
        import cv2
        # Try to create a simple OpenGL context
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imshow('test', img)
        cv2.destroyAllWindows()
        return True
    except ImportError:
        logger.warning("OpenCV not available for OpenGL detection. Install with: pip install opencv-python")
        logger.warning("For better OCR performance, install system dependencies:")
        logger.warning("Ubuntu/Debian: sudo apt install -y libgl1-mesa-glx libglib2.0-0")
        logger.warning("macOS: brew install mesa")
        return False
    except Exception as e:
        logger.warning(f"OpenGL detection failed: {e}")
        logger.warning("For better OCR performance, install system dependencies:")
        logger.warning("Ubuntu/Debian: sudo apt install -y libgl1-mesa-glx libglib2.0-0")
        logger.warning("macOS: brew install mesa")
        return False


class OCRService(ABC):
    """Abstract base class for OCR services."""
    
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as markdown
        """
        pass
    
    @abstractmethod
    def extract_text_with_layout(self, image_path: str) -> str:
        """Extract text with layout awareness from image using OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Layout-aware extracted text as markdown
        """
        pass


class PytesseractOCRService(OCRService):
    """Pytesseract implementation of OCR service with layout detection."""
    
    def __init__(self):
        """Initialize the service."""
        logger.info("PytesseractOCRService initialized")
        self._tesseract_config = '--oem 3 --psm 6'  # Default config for better accuracy
    
    def extract_text(self, image_path: str) -> str:
        """Extract text using pytesseract (simple text extraction)."""
        try:
            # Validate image file
            if not os.path.exists(image_path):
                logger.error(f"Image file does not exist: {image_path}")
                return ""
            
            # Check if file is readable
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    logger.info(f"Image loaded successfully: {img.size} {img.mode}")
            except Exception as e:
                logger.error(f"Failed to load image: {e}")
                return ""
            
            try:
                import pytesseract
                logger.info(f"Running pytesseract on: {image_path}")
                text = pytesseract.image_to_string(image_path, config=self._tesseract_config)
                logger.info(f"Extracted text length: {len(text)}")
                return text.strip()
            except Exception as e:
                logger.error(f"Pytesseract extraction failed: {e}")
                return ""
                
        except Exception as e:
            logger.error(f"Pytesseract extraction failed: {e}")
            return ""
    
    def extract_text_with_layout(self, image_path: str) -> str:
        """Extract text with layout awareness using pytesseract TSV output and pandas."""
        try:
            import pytesseract
            import pandas as pd
            from PIL import Image
            import numpy as np
            import re

            if not os.path.exists(image_path):
                logger.error(f"Image file does not exist: {image_path}")
                return ""

            # Load image
            try:
                img = Image.open(image_path)
            except Exception as e:
                logger.error(f"Failed to load image: {e}")
                return ""

            # Get TSV output as DataFrame
            try:
                df = pytesseract.image_to_data(img, output_type=pytesseract.Output.DATAFRAME, config=self._tesseract_config)
            except Exception as e:
                logger.error(f"pytesseract TSV extraction failed: {e}")
                return ""

            # Remove rows with no text or low confidence
            df = df[df.text.notnull() & (df.text.str.strip() != '') & (df.conf.astype(float) > 30)]
            if df.empty:
                logger.warning("No text found in image (after filtering)")
                return ""

            # Group by block, paragraph, line
            markdown_lines = []
            for (block_num, par_num), block_group in df.groupby(['block_num', 'par_num']):
                # Heuristic: if block is at the top and has large font, treat as header
                block_top = block_group['top'].min()
                avg_height = block_group['height'].mean()
                block_text = ' '.join(block_group['text'])
                is_header = (block_top < 100 and avg_height > 25) or (avg_height > 35)
                if is_header:
                    markdown_lines.append(f"## {block_text}")
                    markdown_lines.append("")
                    continue

                # Try to detect tables: if lines have similar y and regular x spacing
                if self._is_table_block(block_group):
                    table_md = self._block_to_markdown_table(block_group)
                    markdown_lines.append(table_md)
                    markdown_lines.append("")
                    continue

                # Otherwise, group by line
                for line_num, line_group in block_group.groupby('line_num'):
                    line_text = ' '.join(line_group['text'])
                    # Detect lists
                    if self._is_list_item(line_text):
                        markdown_lines.append(f"- {line_text}")
                    else:
                        markdown_lines.append(line_text)
                markdown_lines.append("")

            return '\n'.join(markdown_lines).strip()
        except Exception as e:
            logger.error(f"Pytesseract layout-aware extraction failed: {e}")
            return ""

    def _is_table_block(self, block_group):
        # Heuristic: if block has multiple lines and words are aligned in columns
        if block_group.shape[0] < 6:
            return False
        # Check if there are at least 2 lines with similar number of words
        lines = list(block_group.groupby('line_num'))
        if len(lines) < 2:
            return False
        word_counts = [len(line[1]) for line in lines]
        if min(word_counts) < 2:
            return False
        # Check if x positions are similar across lines (column alignment)
        x_positions = [list(line[1]['left']) for line in lines]
        if len(x_positions) < 2:
            return False
        # Compare columns by rounding x positions
        columns = list(zip(*[np.round(x, -1) for x in x_positions]))
        # If most columns have similar x, treat as table
        col_var = np.std([np.mean(col) for col in columns]) if columns else 100
        return col_var < 50

    def _block_to_markdown_table(self, block_group):
        # Group by line
        lines = [list(line[1].sort_values('left')['text']) for line in block_group.groupby('line_num')]
        if not lines or len(lines) < 2:
            return '\n'.join([' '.join(line) for line in lines])
        # Markdown table: header, separator, rows
        header = '| ' + ' | '.join(lines[0]) + ' |'
        separator = '|' + '|'.join(['---'] * len(lines[0])) + '|'
        rows = ['| ' + ' | '.join(row) + ' |' for row in lines[1:]]
        return '\n'.join([header, separator] + rows)

    def _is_list_item(self, text: str) -> bool:
        """Detect if text is a list item."""
        # Common list indicators
        list_patterns = [
            r'^\d+\.',  # Numbered list
            r'^[•·▪▫◦‣⁃]',  # Bullet points
            r'^[-*+]',  # Markdown list markers
            r'^[a-zA-Z]\.',  # Lettered list
        ]
        
        for pattern in list_patterns:
            if re.match(pattern, text.strip()):
                return True
        
        return False

    def _is_header(self, line: List[Dict]) -> bool:
        """Detect if a line is a header based on font characteristics."""
        if not line:
            return False
        
        # Check if any block in the line has larger font size
        avg_height = sum(block['height'] for block in line) / len(line)
        
        # Headers are typically larger than body text
        return avg_height > 25  # Adjust threshold as needed
    
    def _group_into_lines(self, text_blocks: List[Dict], image_shape: tuple) -> List[List[Dict]]:
        """Group text blocks into lines based on vertical position."""
        if not text_blocks:
            return []
        
        lines = []
        current_line = []
        line_height_threshold = 20  # pixels
        
        for block in text_blocks:
            if not current_line:
                current_line.append(block)
            else:
                # Check if this block is on the same line
                avg_y = sum(b['y'] for b in current_line) / len(current_line)
                if abs(block['y'] - avg_y) <= line_height_threshold:
                    current_line.append(block)
                else:
                    # Start a new line
                    lines.append(current_line)
                    current_line = [block]
        
        # Add the last line
        if current_line:
            lines.append(current_line)
        
        # Sort blocks within each line by x position (left to right)
        for line in lines:
            line.sort(key=lambda x: x['x'])
        
        return lines
    
    def _convert_to_markdown(self, lines: List[List[Dict]]) -> str:
        """Convert lines of text blocks to markdown."""
        markdown_parts = []
        
        for line in lines:
            if not line:
                continue
            
            # Join text in the line
            line_text = ' '.join(block['text'] for block in line)
            
            # Detect headers based on font size and position
            if self._is_header(line):
                markdown_parts.append(f"## {line_text}")
            else:
                # Detect lists
                if self._is_list_item(line_text):
                    markdown_parts.append(f"- {line_text}")
                else:
                    markdown_parts.append(line_text)
            
            markdown_parts.append("")  # Add empty line for spacing
        
        return '\n'.join(markdown_parts).strip()
    
    def _process_layout_data(self, data: Dict, image_shape: tuple) -> str:
        """Process pytesseract layout data and convert to markdown."""
        try:
            # Extract text blocks with their positions
            text_blocks = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                # Filter out empty text and low confidence
                if int(data['conf'][i]) > 30 and data['text'][i].strip():
                    text_blocks.append({
                        'text': data['text'][i].strip(),
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'level': data['level'][i],
                        'conf': data['conf'][i]
                    })
            
            # Sort blocks by vertical position (top to bottom)
            text_blocks.sort(key=lambda x: (x['y'], x['x']))
            
            # Group blocks into lines and paragraphs
            lines = self._group_into_lines(text_blocks, image_shape)
            
            # Convert to markdown
            markdown_text = self._convert_to_markdown(lines)
            
            return markdown_text
            
        except Exception as e:
            logger.error(f"Error processing layout data: {e}")
            return ""


class PaddleOCRService(OCRService):
    """PaddleOCR implementation of OCR service."""
    
    def __init__(self):
        """Initialize the service."""
        logger.info("PaddleOCRService initialized")
        # Cache for PaddleOCR instances
        self._paddle_ocr = None
        self._ppstructure = None
    
    def _get_paddle_ocr(self):
        """Get cached PaddleOCR instance or create new one."""
        if self._paddle_ocr is None:
            try:
                from paddleocr import PaddleOCR
                logger.info("Initializing PaddleOCR for line-based OCR...")
                self._paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
                logger.info("PaddleOCR ready")
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                self._paddle_ocr = None
        return self._paddle_ocr
    
    def _get_ppstructure(self):
        """Get cached PPStructureV3 instance or create new one."""
        if self._ppstructure is None:
            try:
                from paddleocr import PPStructureV3
                logger.info("Initializing PPStructureV3 for layout-aware OCR...")
                self._ppstructure = PPStructureV3(
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False
                )
                logger.info("PPStructureV3 ready")
            except Exception as e:
                logger.error(f"Failed to initialize PPStructureV3: {e}")
                self._ppstructure = None
        return self._ppstructure
    
    def extract_text(self, image_path: str) -> str:
        """Extract text using line-based PaddleOCR."""
        try:
            # Validate image file
            if not os.path.exists(image_path):
                logger.error(f"Image file does not exist: {image_path}")
                return ""
            
            # Check if file is readable
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    logger.info(f"Image loaded successfully: {img.size} {img.mode}")
            except Exception as e:
                logger.error(f"Failed to load image: {e}")
                return ""
            
            try:
                from paddleocr import PaddleOCR
                paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
                logger.info(f"Running PaddleOCR on: {image_path}")
                results = paddle_ocr.ocr(image_path)
                logger.info(f"PaddleOCR results: {results}")
                if results and len(results) > 0:
                    extracted_text = self._simple_text_extraction(results)
                    logger.info(f"Extracted text length: {len(extracted_text)}")
                    return extracted_text
                else:
                    logger.warning("PaddleOCR returned empty results")
            except Exception as e:
                logger.error(f"PaddleOCR line-based extraction failed: {e}")
        except Exception as e:
            logger.error(f"PaddleOCR line-based extraction failed: {e}")
        
        return ""
    
    def extract_text_with_layout(self, image_path: str) -> str:
        """Extract text with layout awareness using PPStructureV3."""
        try:
            # Validate image file
            if not os.path.exists(image_path):
                logger.error(f"Image file does not exist: {image_path}")
                return ""
            
            # Check if file is readable
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    logger.info(f"Image loaded successfully: {img.size} {img.mode}")
            except Exception as e:
                logger.error(f"Failed to load image: {e}")
                return ""
            
            # Try layout-aware OCR first
            try:
                from paddleocr import PPStructureV3
                logger.info("Initializing PPStructureV3 for layout-aware OCR...")
                pipeline = PPStructureV3(
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False
                )
                logger.info(f"Running PPStructureV3 on: {image_path}")
                results = pipeline.predict(input=image_path)
                logger.info(f"PPStructureV3 results type: {type(results)}, length: {len(results) if results else 0}")
                if results and len(results) > 0:
                    logger.info(f"PPStructureV3 returned {len(results)} results")
                    extracted_text = self._extract_text_with_layout(results)
                    logger.info(f"Layout-aware extracted text length: {len(extracted_text)}")
                    return extracted_text
                else:
                    logger.warning("PPStructureV3 returned empty results")
            except Exception as e:
                logger.warning(f"Layout-aware OCR failed: {e}, falling back to line-based OCR")
            
            # Fallback to line-based OCR
            logger.info("Falling back to line-based OCR")
            return self.extract_text(image_path)
            
        except Exception as e:
            logger.error(f"PaddleOCR layout-aware extraction failed: {e}")
            return ""
    
    def _extract_text_with_layout(self, results) -> str:
        """Extract text from PPStructureV3 results with layout awareness."""
        try:
            logger.info(f"Processing layout results: {type(results)}")
            if not results or len(results) == 0:
                logger.warning("No layout results to process")
                return ""
            
            # Handle PPStructureV3 results format
            markdown_parts = []
            for res in results:
                if hasattr(res, 'markdown') and res.markdown:
                    md = res.markdown.get('markdown_texts', '')
                    if md:
                        logger.info(f"Found markdown text, length: {len(md)}")
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
                result = "\n\n".join(markdown_parts)
                logger.info(f"Extracted layout text length: {len(result)}")
                return result
            else:
                logger.warning("No markdown parts extracted from layout results")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text with layout: {e}")
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
        
        # Remove HTML img tags and other HTML elements
        text = re.sub(r'<img[^>]*>', '', text)
        text = re.sub(r'<[^>]*>', '', text)
        
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
        
        # Clean up bullet points and lists
        text = re.sub(r'•\s*', '- ', text)
        
        return text.strip()
    
    def _simple_text_extraction(self, results) -> str:
        """Extract text from line-based OCR results."""
        try:
            logger.info(f"Processing simple OCR results: {type(results)}")
            if not results or len(results) == 0:
                logger.warning("No simple OCR results to process")
                return ""
            
            text_lines = []
            
            # Handle different result formats
            if isinstance(results, list):
                logger.info(f"Processing list of {len(results)} OCR results")
                for i, line in enumerate(results):
                    logger.info(f"Processing line {i}: {type(line)}")
                    if line and len(line) > 0:
                        for word_info in line:
                            if len(word_info) >= 2:
                                text_lines.append(word_info[1][0])
            elif isinstance(results, dict):
                # Handle dict format
                logger.info("Processing dict OCR results")
                if 'text' in results:
                    text_lines.append(results['text'])
            
            extracted_text = '\n'.join(text_lines)
            logger.info(f"Simple extraction result: {extracted_text}")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error in simple text extraction: {e}")
            return ""
    
    def _convert_to_layout_markdown(self, text_blocks: List[Dict]) -> str:
        """Convert text blocks to layout-aware markdown."""
        try:
            from llm_converter.config import InternalConfig
            from markdownify import markdownify as md
            
            headers = []
            paragraphs = []
            tables = []
            lists = []
            
            for block in text_blocks:
                text = block.get('text', '').strip()
                block_type = block.get('type', 'text')
                
                if not text:
                    continue
                
                if block_type == 'title' or block_type == 'header':
                    headers.append(text)
                elif block_type == 'table':
                    if InternalConfig.use_markdownify:
                        tables.append(md(text, heading_style="ATX"))
                    else:
                        tables.append(text)
                elif block_type == 'list':
                    lists.append(text)
                else:
                    paragraphs.append(text)
            
            content_parts = []
            
            # Add headers
            for header in headers:
                content_parts.append(f"# {header}")
                content_parts.append("")
            
            # Add paragraphs
            for paragraph in paragraphs:
                content_parts.append(paragraph)
                content_parts.append("")
            
            # Add lists
            for list_item in lists:
                content_parts.append(f"- {list_item}")
                content_parts.append("")
            
            # Add tables
            for table in tables:
                content_parts.append(table)
                content_parts.append("")
            
            return '\n'.join(content_parts)
            
        except Exception as e:
            logger.error(f"Error converting to layout markdown: {e}")
            return '\n\n'.join([block.get('text', '') for block in text_blocks])


class OCRServiceFactory:
    """Factory for creating OCR services based on configuration."""
    
    @staticmethod
    def create_service(provider: str = None) -> OCRService:
        """Create OCR service based on provider configuration.
        
        Args:
            provider: OCR provider name (defaults to config)
            
        Returns:
            OCRService instance
        """
        from llm_converter.config import InternalConfig
        
        if provider is None:
            provider = getattr(InternalConfig, 'ocr_provider', 'paddleocr')
        
        if provider.lower() == 'paddleocr':
            return PaddleOCRService()
        elif provider.lower() == 'pytesseract':
            return PytesseractOCRService()
        else:
            raise ValueError(f"Unsupported OCR provider: {provider}")
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available OCR providers.
        
        Returns:
            List of available provider names
        """
        return ['paddleocr', 'pytesseract']  # Add more providers here as they're implemented 