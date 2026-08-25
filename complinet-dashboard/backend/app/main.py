from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import compliance, devices

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compliance.router)
app.include_router(devices.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the CompliNet API!"}