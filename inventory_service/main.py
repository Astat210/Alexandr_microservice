from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routing.routes import router
from connection.postgres import init_db

app = FastAPI(title="SkifTradeInventory Microservice")
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    init_db()