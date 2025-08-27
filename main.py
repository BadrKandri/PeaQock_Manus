import sys, os, shutil, logging, uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import dashboard, upload, download, streaming
from core.paths import output_path

# Import routers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("peaqock_api")

app = FastAPI(
    title="PeaQock Manus API",
    description="API for PeaQock_Manus Agent",
    version="1.0.0"
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(upload.router, tags=["upload"])
app.include_router(download.router, tags=["download"])  
app.include_router(streaming.router, tags=["streaming"])

if output_path.exists():
    try:
        shutil.rmtree(output_path)
        logger.info("Cleaned output folder on startup")
    except PermissionError:
        logger.warning("Could not clean output folder - in use by another process")
    except Exception as e:
        logger.warning(f"Could not clean output folder: {e}")

if __name__ == "__main__":
    print("API server starting at http://127.0.0.1:8000/")
    uvicorn.run(app, host="127.0.0.1", port=8000, access_log=False)
