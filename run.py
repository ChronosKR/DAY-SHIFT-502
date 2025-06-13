#!/usr/bin/env python3

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from plc_scada_lab.backend.api import app
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    print("and that all dependencies are installed in your virtual environment.")
    sys.exit(1)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("🏭 Starting PLC SCADA Lab...")
    print(f"🌐 Server will be available at: http://localhost:{port}")
    print("📚 Select a lesson from the sidebar to begin learning!")
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            reload=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down PLC SCADA Lab...")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)