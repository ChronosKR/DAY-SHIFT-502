#!/usr/bin/env python3

import os
import sys
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        # Import the FastAPI app
        from plc_scada_lab.backend.api import app
        
        # Get port from environment or default to 8000
        port = int(os.getenv("PORT", "8000"))
        
        logger.info(f"Starting PLC SCADA Lab on port {port}")
        
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()