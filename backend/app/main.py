from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
  title=settings.PROJECT_NAME,
  openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware (Cross-Origin Resource Sharing)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Import and include routers
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
  """
  Root endpoint to verify the backend is running.
  """
  return {"message": "Welcome to Cosmetics Chatbot Assistant API", "status": "running"}

@app.get("/health")
async def health_check():
  """
  Health check endpoint for Docker/Kubernetes probes.
  """
  # TODO: Add logic to check DB connection status here
  return {"status": "healthy"}

if __name__ == "__main__":
  import uvicorn
  # This block allows running with `python app/main.py`
  uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
