from fastapi import FastAPI
from app.routes import process
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Claim Processing Pipeline")

app.include_router(process.router)

@app.get("/")
def root():
    return {"message": "Claim Processing Pipeline API"}
