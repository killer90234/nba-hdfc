from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.routers import auth, customers, recommendations, dashboard, products

settings = get_settings()

app = FastAPI(
    title="HDFC AI Next Best Product Advisor (NBA 2.0)",
    description="AI-powered Relationship Manager Portal for HDFC Bank product recommendations",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(recommendations.router)
app.include_router(dashboard.router)
app.include_router(products.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    try:
        from seed import seed
        seed()
    except Exception as e:
        print(f"Seed error: {e}")


@app.get("/")
def root():
    return {
        "name": "HDFC AI Next Best Product Advisor (NBA 2.0)",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "hdfc-nba-2.0"}
