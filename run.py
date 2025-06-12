import uvicorn
# import path includes the package name because everything lives under plc_scada_lab
from plc_scada_lab.backend import api  # noqa: F401
if __name__ == "__main__":
    uvicorn.run("plc_scada_lab.backend.api:app",
                host="127.0.0.1", port=8000, log_level="info")
