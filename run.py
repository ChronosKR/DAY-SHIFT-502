# run.py  (replace just these two lines)

import os, uvicorn
from backend.api import app  # ← fixed import

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        app,  # ← use imported app directly
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
