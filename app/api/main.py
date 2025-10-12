from fastapi import FastAPI

from routers import country, state

app = FastAPI(
    title="Country API",
    description="CRUD API for managing countries and states/provinces with event logging (Transactional Outbox pattern)",
    version="1.0.0",
)

# Register routers
app.include_router(country.router)
app.include_router(state.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
