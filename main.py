from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title='Grammar Checker API')
app.include_router(router)