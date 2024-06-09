from contextlib import asynccontextmanager

from fastapi import FastAPI

from route_chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    print("Starting up...")
    yield
    # Shutdown code here
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

app.include_router(chat_router)
