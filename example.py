#!/usr/bin/env python3
from llm_converter import FileConverter


file_path = "sample_documents/sample.pdf"

converter = FileConverter(
    cloud_mode=True,
    api_key="<api-key>"
)

result = converter.convert(file_path).to_markdown()
print("📝=============================== Markdown Output:===============================")
print(result)

result = converter.convert(file_path).to_html()
print("📝=============================== HTML Output:===============================")
print(result)

result = converter.convert(file_path).to_json()
print("📝=============================== JSON Output:===============================")
print(result)

result = converter.convert(file_path).to_text()

print("📝=============================== Markdown Output:===============================")
print(result)
