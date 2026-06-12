from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, races, predictions, model, ai

app = FastAPI(
    title="F1 Quali Predictor API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://f1-quali-predictor-web.onrender.com",
    ],
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(races.router, prefix="/races", tags=["Races"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
app.include_router(model.router, prefix="/model", tags=["Model"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])