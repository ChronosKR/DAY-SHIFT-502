# run.py  (replace just these two lines)

import os, uvicorn
from backend import api  # ← changed

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "backend.api:app",  # ← changed
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
