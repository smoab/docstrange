"""Conversion result class for handling different output formats."""

import json
from typing import Any, Dict, List, Optional, Union


class ConversionResult:
    """Result object with methods to export to different formats."""
    
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Initialize the conversion result.
        
        Args:
            content: The converted content as string
            metadata: Optional metadata about the conversion
        """
        self.content = content
        self.metadata = metadata or {}
    
    def to_markdown(self) -> str:
        """Export as markdown.
        
        Returns:
            The content formatted as markdown
        """
        return self.content
    
    def to_html(self) -> str:
        """Export as HTML.
        
        Returns:
            The content formatted as HTML
        """
        # Convert markdown-like content to HTML
        html_content = self.content
        
        # Basic markdown to HTML conversion
        html_content = html_content.replace('\n\n', '</p><p>')
        html_content = html_content.replace('\n', '<br>')
        
        # Handle headers
        for i in range(6, 0, -1):
            html_content = html_content.replace('#' * i + ' ', f'<h{i}>')
            html_content = html_content.replace('\n' + '#' * i + ' ', f'</h{i}>\n<h{i}>')
        
        # Wrap in HTML structure
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Converted Document</title>
    <style>
        body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; margin: 2rem; }}
        h1, h2, h3, h4, h5, h6 {{ color: #1D2554; margin-top: 2rem; margin-bottom: 1rem; }}
        p {{ margin-bottom: 1rem; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
        th, td {{ border: 1px solid #EAEDFF; padding: 0.5rem; text-align: left; }}
        th {{ background-color: #F2F4FF; color: #1D2554; }}
        code {{ background-color: #F8FAFF; padding: 0.2rem 0.4rem; border-radius: 3px; }}
        pre {{ background-color: #F8FAFF; padding: 1rem; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="content">
        {html_content}
    </div>
</body>
</html>"""
    
    def to_json(self) -> Dict[str, Any]:
        """Export as JSON.
        
        Returns:
            Dictionary containing content and metadata
        """
        return {
            "content": self.content,
            "metadata": self.metadata,
            "format": "json"
        }
    
    def to_text(self) -> str:
        """Export as plain text.
        
        Returns:
            The content as plain text
        """
        return self.content
    
    def __str__(self) -> str:
        """String representation of the result."""
        return self.content
    
    def __repr__(self) -> str:
        """Representation of the result object."""
        return f"ConversionResult(content='{self.content[:50]}...', metadata={self.metadata})" 