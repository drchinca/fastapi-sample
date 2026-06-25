from fastapi import FastAPI

from ssfs import router

app = FastAPI(title="Random User POC", version="1.0.0")
app.include_router(router)
