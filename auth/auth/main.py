from fastapi import FastAPI

from auth.api.v1 import router as api_v1

app = FastAPI(title="AuthSVC")
app.include_router(api_v1, prefix="/v1")

def run() -> None:
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
