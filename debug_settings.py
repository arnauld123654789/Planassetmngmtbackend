import sys
import os
# Add current directory to path
sys.path.append(os.getcwd())

try:
    from app.core.config import Settings
    settings = Settings()
    print("Settings loaded successfully!")
    print(f"Project: {settings.PROJECT_NAME}")
    print(f"DB: {settings.DATABASE_URL}")
except Exception as e:
    print(f"Error loading settings: {e}")
    import traceback
    traceback.print_exc()
