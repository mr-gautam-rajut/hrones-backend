from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your route modules
from app.routes import products, orders

app = FastAPI()

# Allow frontend and other domains to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- ROUTES ----------
@app.get("/")
async def root():
    return {"message": "Backend running ✅"}

app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
