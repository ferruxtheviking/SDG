import os
from fastapi import FastAPI
from config.middlewares import CorsMiddleware,JWTAuthMiddleware
from config.endpoints import endpoints

# Initialize FastAPI
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Define the middlewares
app.add_middleware(JWTAuthMiddleware)
app.add_middleware(CorsMiddleware)

app.include_router(endpoints)

if __name__ == "__main__":
    from uvicorn import run
    run(app, host = '0.0.0.0', port = 81)