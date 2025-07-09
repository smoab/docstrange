"""Tests for the llm-data-converter library."""

import os
import tempfile
import pytest

from llm_converter import FileConverter, ConversionError, UnsupportedFormatError


class TestFileConverter:
    """Test cases for FileConverter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = FileConverter()
    
    def test_convert_text_file(self):
        """Test converting a text file."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test text file.\n\nIt has multiple lines.")
            temp_file = f.name
        
        try:
            result = self.converter.convert(temp_file)
            content = result.to_markdown()
            
            assert "This is a test text file" in content
            assert "It has multiple lines" in content
            assert result.metadata is not None
        finally:
            os.unlink(temp_file)
    
    def test_convert_text(self):
        """Test converting plain text."""
        text = "This is plain text for testing."
        result = self.converter.convert_text(text)
        
        assert result.to_markdown() == text
        assert result.to_text() == text
        assert result.metadata["content_type"] == "text"
    
    def test_convert_url(self):
        """Test converting a URL."""
        # Use a simple test URL
        url = "https://httpbin.org/html"
        result = self.converter.convert_url(url)
        
        assert result.metadata["url"] == url
        assert result.metadata["status_code"] == 200
    
    def test_unsupported_format(self):
        """Test handling of unsupported formats."""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b"test content")
            temp_file = f.name
        
        try:
            with pytest.raises(UnsupportedFormatError):
                self.converter.convert(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_file_not_found(self):
        """Test handling of non-existent files."""
        with pytest.raises(FileNotFoundError):
            self.converter.convert("nonexistent_file.txt")
    
    def test_supported_formats(self):
        """Test getting supported formats."""
        formats = self.converter.get_supported_formats()
        
        assert '.txt' in formats
        assert '.pdf' in formats
        assert '.docx' in formats
        assert '.xlsx' in formats
        assert '.html' in formats
        assert 'URLs' in formats
    
    def test_output_formats(self):
        """Test different output formats."""
        text = "Test content"
        result = self.converter.convert_text(text)
        
        # Test markdown output
        markdown = result.to_markdown()
        assert markdown == text
        
        # Test HTML output
        html = result.to_html()
        assert "DOCTYPE html" in html
        assert text in html
        
        # Test JSON output
        json_output = result.to_json()
        assert json_output["content"] == text
        assert json_output["format"] == "json"
        
        # Test text output
        text_output = result.to_text()
        assert text_output == text
    
    def test_converter_configuration(self):
        """Test converter configuration options."""
        converter = FileConverter(
            preserve_layout=False,
            include_images=True,
            ocr_enabled=True
        )
        
        assert converter.preserve_layout is False
        assert converter.include_images is True
        assert converter.ocr_enabled is True


class TestConversionResult:
    """Test cases for ConversionResult class."""
    
    def test_result_creation(self):
        """Test creating a conversion result."""
        content = "Test content"
        metadata = {"test": "value"}
        
        result = ConversionResult(content, metadata)
        
        assert result.content == content
        assert result.metadata == metadata
    
    def test_result_string_representation(self):
        """Test string representation of result."""
        content = "Test content"
        result = ConversionResult(content)
        
        assert str(result) == content
        assert repr(result).startswith("ConversionResult")
    
    def test_result_without_metadata(self):
        """Test result creation without metadata."""
        content = "Test content"
        result = ConversionResult(content)
        
        assert result.content == content
        assert result.metadata == {}


if __name__ == "__main__":
    pytest.main([__file__]) 