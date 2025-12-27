from docling.document_converter import DocumentConverter


converter = DocumentConverter()
result = converter.convert("https://bunseki.jsac.jp/wp-content/uploads/2021/05/2021_05_p236.%E6%8A%80%E8%A1%93%E7%B4%B9%E4%BB%8B_%E6%97%A5%E7%AB%8B%E3%83%8F%E3%82%A4%E3%83%86%E3%82%AF%E3%82%B5%E3%82%A4%E3%82%A8%E3%83%B3%E3%82%B9.pdf").document
print(result.export_to_markdown())

    