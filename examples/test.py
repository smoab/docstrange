#!/usr/bin/env python3
from document_extractor import FileConverter


file_path = "sample_documents/sample.png"

converter = FileConverter()

result = converter.convert(file_path).to_markdown()

print("📝=============================== Markdown Output:===============================")
print(result)
