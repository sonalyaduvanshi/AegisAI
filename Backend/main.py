from fastapi import FastAPI

app = FastAPI(
    title="AegisAI",
    description="Agentic Production Incident Intelligence Platform"
)


@app.get("/")
def home():
    return {
        "message": "AegisAI backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }