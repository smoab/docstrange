"""URL processor for handling web pages."""

import re
from typing import Dict, Any
from urllib.parse import urlparse

from .base import BaseProcessor
from ..result import ConversionResult
from ..exceptions import ConversionError, NetworkError


class URLProcessor(BaseProcessor):
    """Processor for URLs and web pages."""
    
    def can_process(self, file_path: str) -> bool:
        """Check if this processor can handle the given file.
        
        Args:
            file_path: Path to the file to check (or URL)
            
        Returns:
            True if this processor can handle the file
        """
        # Check if it looks like a URL
        return self._is_url(file_path)
    
    def process(self, file_path: str) -> ConversionResult:
        """Process the URL and return a conversion result.
        
        Args:
            file_path: URL to process
            
        Returns:
            ConversionResult containing the processed content
            
        Raises:
            NetworkError: If network operations fail
            ConversionError: If processing fails
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Fetch the web page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(file_path, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            content_parts = []
            
            # Get title
            title = soup.find('title')
            if title:
                content_parts.append(f"# {title.get_text().strip()}\n")
            
            # Get main content
            main_content = self._extract_main_content(soup)
            if main_content:
                content_parts.append(main_content)
            else:
                # Fallback to body text
                body = soup.find('body')
                if body:
                    content_parts.append(body.get_text())
            
            content = '\n'.join(content_parts)
            
            # Clean up the content
            content = self._clean_content(content)
            
            metadata = {
                "url": file_path,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "content_length": len(response.content),
                "processor": self.__class__.__name__
            }
            
            return ConversionResult(content, metadata)
            
        except ImportError:
            raise ConversionError("requests and beautifulsoup4 are required for URL processing. Install them with: pip install requests beautifulsoup4")
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch URL {file_path}: {str(e)}")
        except Exception as e:
            if isinstance(e, (NetworkError, ConversionError)):
                raise
            raise ConversionError(f"Failed to process URL {file_path}: {str(e)}")
    
    def _is_url(self, text: str) -> bool:
        """Check if the text looks like a URL.
        
        Args:
            text: Text to check
            
        Returns:
            True if text looks like a URL
        """
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False
    
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
                return element.get_text()
        
        # If no main content found, return empty string
        return ""
    
    def _clean_content(self, content: str) -> str:
        """Clean up the extracted web content.
        
        Args:
            content: Raw web text content
            
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