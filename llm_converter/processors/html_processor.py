"""HTML file processor."""

import os
import logging
from typing import Dict, Any

from .base import BaseProcessor
from ..result import ConversionResult
from ..exceptions import ConversionError, FileNotFoundError

# Configure logging
logger = logging.getLogger(__name__)


class HTMLProcessor(BaseProcessor):
    """Processor for HTML files."""
    
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
        return ext in ['.html', '.htm', '.xhtml']
    
    def process(self, file_path: str) -> ConversionResult:
        """Process the HTML file and return a conversion result.
        
        Args:
            file_path: Path to the HTML file to process
            
        Returns:
            ConversionResult containing the processed content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ConversionError: If processing fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            from bs4 import BeautifulSoup
            
            metadata = self.get_metadata(file_path)
            content_parts = []
            
            # Read the HTML file
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content with better structure preservation
            content_parts = self._extract_structured_content(soup)
            
            content = "\n\n".join(content_parts)
            
            # Clean up the content
            content = self._clean_content(content)
            
            return ConversionResult(content, metadata)
            
        except ImportError:
            raise ConversionError("beautifulsoup4 is required for HTML processing. Install it with: pip install beautifulsoup4")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, ConversionError)):
                raise
            raise ConversionError(f"Failed to process HTML file {file_path}: {str(e)}")
    
    def _extract_structured_content(self, soup) -> list:
        """Extract structured content from HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of content parts
        """
        content_parts = []
        
        # Get title
        title = soup.find('title')
        if title:
            content_parts.append(f"# {title.get_text().strip()}")
        
        # Process main content areas
        main_content = self._extract_main_content(soup)
        if main_content:
            content_parts.append(main_content)
        else:
            # Fallback to body text
            body = soup.find('body')
            if body:
                content_parts.append(self._process_body_content(body))
        
        return content_parts
    
    def _extract_main_content(self, soup) -> str:
        """Extract main content from the HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted main content
        """
        # Try to find main content areas
        main_selectors = [
            'main',
            '[role="main"]',
            '.main-content',
            '.content',
            '#content',
            'article',
            '.post-content',
            '.entry-content'
        ]
        
        for selector in main_selectors:
            element = soup.select_one(selector)
            if element:
                return self._process_body_content(element)
        
        # If no main content found, return empty string
        return ""
    
    def _process_body_content(self, element) -> str:
        """Process body content with structure preservation.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Processed content
        """
        content_parts = []
        
        for child in element.children:
            if child.name:
                if child.name.startswith('h'):
                    level = int(child.name[1])
                    text = child.get_text().strip()
                    if text:
                        content_parts.append(f"{'#' * level} {text}")
                elif child.name == 'p':
                    text = child.get_text().strip()
                    if text:
                        content_parts.append(text)
                elif child.name in ['ul', 'ol']:
                    for li in child.find_all('li', recursive=False):
                        text = li.get_text().strip()
                        if text:
                            content_parts.append(f"- {text}")
                elif child.name == 'table':
                    table_content = self._convert_table_to_markdown(child)
                    if table_content:
                        content_parts.append(table_content)
                elif child.name in ['div', 'section', 'article']:
                    # Recursively process nested content
                    nested_content = self._process_body_content(child)
                    if nested_content.strip():
                        content_parts.append(nested_content)
        
        return "\n\n".join(content_parts)
    
    def _convert_table_to_markdown(self, table_element) -> str:
        """Convert HTML table to markdown table.
        
        Args:
            table_element: BeautifulSoup table element
            
        Returns:
            Markdown table string
        """
        rows = table_element.find_all('tr')
        if not rows:
            return ""
        
        table_parts = []
        
        # Process header row
        header_cells = rows[0].find_all(['th', 'td'])
        if header_cells:
            header_text = [cell.get_text().strip() for cell in header_cells]
            table_parts.append("| " + " | ".join(header_text) + " |")
            table_parts.append("| " + " | ".join(["---"] * len(header_cells)) + " |")
        
        # Process data rows
        for row in rows[1:]:
            cells = row.find_all(['th', 'td'])
            if cells:
                cell_text = [cell.get_text().strip() for cell in cells]
                table_parts.append("| " + " | ".join(cell_text) + " |")
        
        return "\n".join(table_parts)
    
    def _clean_content(self, content: str) -> str:
        """Clean up the extracted HTML content.
        
        Args:
            content: Raw HTML text content
            
        Returns:
            Cleaned text content
        """
        # Remove excessive whitespace and normalize
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive whitespace
            line = ' '.join(line.split())
            if line.strip():
                cleaned_lines.append(line)
        
        # Join lines and add proper spacing
        content = '\n'.join(cleaned_lines)
        
        # Add spacing around headers
        content = content.replace('# ', '\n# ')
        content = content.replace('## ', '\n## ')
        
        return content.strip() 