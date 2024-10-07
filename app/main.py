from fastapi import FastAPI
from api.webhook_controller import router as webhook_router

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


app.include_router(webhook_router)
