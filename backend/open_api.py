import json
from src.app.main import app

openapi_data = app.openapi()

# ファイルとして保存（フロントエンドから見える場所に置くと便利）
with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(openapi_data, f, indent=2, ensure_ascii=False)

print("✅ openapi.json generated successfully!")