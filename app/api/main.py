from fastapi import FastAPI
from routers import country

app = FastAPI(
    title="Country API",
    description="CRUD API for managing countries with event logging (Transactional Outbox pattern)",
    version="1.0.0"
)

# ルーターの登録
app.include_router(country.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
