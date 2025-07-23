"""Cloud processor for Nanonets API integration."""

import os
import requests
import json
import logging
from typing import Dict, Any, Optional

from .base import BaseProcessor
from ..result import ConversionResult
from ..exceptions import ConversionError

logger = logging.getLogger(__name__)


class CloudConversionResult(ConversionResult):
    """Enhanced ConversionResult for cloud mode with support for different API output types."""
    
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None, api_output_type: str = "markdown", 
                 cloud_processor: Optional['CloudProcessor'] = None, file_path: Optional[str] = None):
        super().__init__(content, metadata)
        self.api_output_type = api_output_type
        self.cloud_processor = cloud_processor
        self.file_path = file_path
        self._cached_outputs = {api_output_type: content}  # Cache the original output
    
    def _get_cloud_output(self, output_type: str) -> str:
        """Get output from cloud API for specific type, with caching."""
        if output_type in self._cached_outputs:
            return self._cached_outputs[output_type]
        
        if not self.cloud_processor or not self.file_path:
            # Fallback to local conversion if cloud processor not available
            return self._convert_locally(output_type)
        
        try:
            # Create a new processor with the desired output type
            temp_processor = CloudProcessor(
                api_key=self.cloud_processor.api_key,
                output_type=output_type,
                model_type=self.cloud_processor.model_type,  # Pass model_type
                preserve_layout=self.cloud_processor.preserve_layout,
                include_images=self.cloud_processor.include_images
            )
            
            # Make API call for specific output type
            result = temp_processor.process(self.file_path)
            content = result.content
            
            # Cache the result
            self._cached_outputs[output_type] = content
            return content
            
        except Exception as e:
            logger.warning(f"Failed to get {output_type} from cloud API: {e}. Using local conversion.")
            return self._convert_locally(output_type)
    
    def _convert_locally(self, output_type: str) -> str:
        """Fallback to local conversion methods."""
        if output_type == "html":
            return super().to_html()
        elif output_type == "flat-json":
            return json.dumps(super().to_json(), indent=2)
        else:
            return self.content
    
    def to_markdown(self) -> str:
        """Export as markdown."""
        if self.api_output_type == "markdown":
            return self.content
        else:
            # Request markdown from cloud API
            return self._get_cloud_output("markdown")
    
    def to_html(self) -> str:
        """Export as HTML."""
        if self.api_output_type == "html":
            return self.content
        else:
            # Request HTML from cloud API
            return self._get_cloud_output("html")
    
    def to_json(self) -> Dict[str, Any]:
        """Export as structured JSON."""
        if self.api_output_type == "flat-json":
            try:
                parsed_content = json.loads(self.content)
                return {
                    "document": parsed_content,
                    "conversion_metadata": self.metadata,
                    "format": "cloud_flat_json"
                }
            except:
                return {
                    "document": {"raw_content": self.content},
                    "conversion_metadata": self.metadata,
                    "format": "cloud_flat_json_raw"
                }
        else:
            # Request JSON from cloud API
            json_content = self._get_cloud_output("flat-json")
            try:
                parsed_content = json.loads(json_content)
                return {
                    "document": parsed_content,
                    "conversion_metadata": self.metadata,
                    "format": "cloud_flat_json"
                }
            except:
                return {
                    "document": {"raw_content": json_content},
                    "conversion_metadata": self.metadata,
                    "format": "cloud_flat_json_raw"
                }
    
    def to_text(self) -> str:
        """Export as plain text."""
        if self.api_output_type == "flat-json":
            try:
                data = json.loads(self.content)
                if isinstance(data, dict):
                    text_parts = []
                    for key, value in data.items():
                        if isinstance(value, str) and key.lower() in ['text', 'content', 'body', 'extracted_text']:
                            text_parts.append(value)
                    if text_parts:
                        return '\n\n'.join(text_parts)
                    else:
                        text_parts = [str(v) for v in data.values() if isinstance(v, str)]
                        return '\n'.join(text_parts)
                elif isinstance(data, list):
                    return '\n'.join(str(item) for item in data if isinstance(item, str))
                else:
                    return str(data)
            except:
                return self.content
        elif self.api_output_type == "html":
            import re
            text = re.sub(r'<[^>]+>', '', self.content)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        else:
            return self.content


class CloudProcessor(BaseProcessor):
    """Processor for cloud-based document conversion using Nanonets API."""
    
    def __init__(self, api_key: str, output_type: str = "markdown", model_type: Optional[str] = None, **kwargs):
        """Initialize cloud processor.
        
        Args:
            api_key: Nanonets API key
            output_type: API output type (markdown, flat-json, html)
            model_type: Model type for cloud processing (gemini, openapi)
        """
        super().__init__(**kwargs)
        self.api_key = api_key
        self.output_type = output_type
        self.model_type = model_type
        self.api_url = "https://extraction-api.nanonets.com/extract"
        
        # Validate output type
        valid_output_types = ["markdown", "flat-json", "html"]
        if output_type not in valid_output_types:
            logger.warning(f"Invalid output type '{output_type}' for cloud API. Using 'markdown'.")
            self.output_type = "markdown"
    
    def can_process(self, file_path: str) -> bool:
        """Check if the processor can handle the file."""
        if not self.api_key:
            return False
            
        # Cloud processor supports most common document formats
        supported_extensions = {
            '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', 
            '.txt', '.html', '.htm', '.png', '.jpg', '.jpeg', '.gif', 
            '.bmp', '.tiff', '.tif'
        }
        
        _, ext = os.path.splitext(file_path.lower())
        return ext in supported_extensions
    
    def process(self, file_path: str) -> CloudConversionResult:
        """Process file using Nanonets cloud API.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            CloudConversionResult with processed content
            
        Raises:
            ConversionError: If processing fails
        """
        if not os.path.exists(file_path):
            raise ConversionError(f"File not found: {file_path}")
        
        if not self.api_key:
            raise ConversionError(
                "API key required for cloud processing. "
                "Get your API key from https://app.nanonets.com/#/keys"
            )
        
        try:
            # Prepare authentication header - using Bearer token
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # Prepare file for upload
            with open(file_path, 'rb') as file:
                files = {
                    'file': (os.path.basename(file_path), file, self._get_content_type(file_path))
                }
                
                data = {
                    'output_type': self.output_type
                }
                
                # Add model_type if specified
                if self.model_type:
                    data['model_type'] = self.model_type
                
                # Log the request details
                log_msg = f"Processing {file_path} with Nanonets cloud API (output_type={self.output_type}"
                if self.model_type:
                    log_msg += f", model_type={self.model_type}"
                log_msg += ")..."
                logger.info(log_msg)
                
                # Make API request
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=300
                )
                
                response.raise_for_status()
                result_data = response.json()
                
                # Extract content from response
                content = self._extract_content_from_response(result_data)
                
                # Create metadata
                metadata = {
                    'source_file': file_path,
                    'processing_mode': 'cloud',
                    'api_provider': 'nanonets',
                    'output_type': self.output_type,
                    'file_size': os.path.getsize(file_path),
                    'api_response_status': response.status_code
                }
                
                logger.info(f"Successfully processed {file_path} using cloud API")
                
                return CloudConversionResult(
                    content=content, 
                    metadata=metadata, 
                    api_output_type=self.output_type,
                    cloud_processor=self,
                    file_path=file_path
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Cloud API request failed: {e}")
            raise ConversionError(f"Cloud API request failed: {e}")
        except Exception as e:
            logger.error(f"Cloud processing failed: {e}")
            raise ConversionError(f"Cloud processing failed: {e}")
    
    def _extract_content_from_response(self, response_data: Dict[str, Any]) -> str:
        """Extract content from API response based on output type."""
        try:
            if self.output_type == "flat-json":
                # For JSON output, try to find structured data
                if 'flat_json' in response_data:
                    return json.dumps(response_data['flat_json'], indent=2)
                elif 'json' in response_data:
                    return json.dumps(response_data['json'], indent=2)
                elif 'structured_data' in response_data:
                    return json.dumps(response_data['structured_data'], indent=2)
                elif 'data' in response_data and isinstance(response_data['data'], dict):
                    return json.dumps(response_data['data'], indent=2)
            
            elif self.output_type == "html":
                # For HTML output, try to find HTML content
                if 'html' in response_data:
                    return response_data['html']
                elif 'html_content' in response_data:
                    return response_data['html_content']
            
            # For markdown or fallback, try common content keys
            content_keys = ['content', 'text', 'extracted_text', 'markdown', 'result', 'data']
            
            for key in content_keys:
                if key in response_data:
                    value = response_data[key]
                    if isinstance(value, str):
                        return value
                    elif isinstance(value, dict):
                        for sub_key in ['content', 'text', 'markdown', 'extracted_text']:
                            if sub_key in value:
                                return str(value[sub_key])
                        return json.dumps(value, indent=2)
                    elif isinstance(value, list):
                        if all(isinstance(item, str) for item in value):
                            return '\n'.join(value)
                        else:
                            return json.dumps(value, indent=2)
            
            # Fallback: return whole response as JSON
            logger.warning("Could not find content in expected API response keys, returning full response")
            return json.dumps(response_data, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to extract content from API response: {e}")
            return json.dumps(response_data, indent=2)
    
    def _get_content_type(self, file_path: str) -> str:
        """Get content type for file upload."""
        _, ext = os.path.splitext(file_path.lower())
        
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        }
        
        return content_types.get(ext, 'application/octet-stream') 