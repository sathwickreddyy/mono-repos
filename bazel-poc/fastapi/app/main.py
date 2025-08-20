from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import items
import uvicorn

app = FastAPI(title="Python FastAPI Service", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router, prefix="/api", tags=["items"])

@app.get("/")
async def root():
    return {"message": "FastAPI service running in Bazel monorepo"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
