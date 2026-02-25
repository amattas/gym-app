from fastapi import FastAPI

from gym_api.routers.summaries import router as summaries_router

app = FastAPI(title="Gym API", version="0.1.0")
app.include_router(summaries_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
