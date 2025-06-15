from fastapi import FastAPI
from routing.routes import router
from connection.postgres import init_db

app = FastAPI(title="SkifTradeInventory Microservice")
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    init_db()