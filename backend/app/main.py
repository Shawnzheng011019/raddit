from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import recommend, user, post

app = FastAPI(title="Raddit Recommendation System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommend.router, prefix="/api/recommend", tags=["recommend"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(post.router, prefix="/api/post", tags=["post"])

@app.get("/")
async def root():
    return {"message": "Welcome to Raddit Recommendation System"}