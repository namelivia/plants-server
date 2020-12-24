from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from app.plants.api import router as plants
from app.images.api import router as images
import logging
import sys

Base.metadata.create_all(bind=engine)

app = FastAPI()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

origins = [
    'http://localhost:8080',
    'http://plants.namelivia.com'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

[app.include_router(router) for router in [
    plants,
    images
]]
