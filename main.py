import os, time, datetime
from importlib import import_module
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from typing import List, Annotated
from starlette.responses import HTMLResponse
import models
import settings

from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

#import routes
routes_list = []
for file in os.listdir("./routes"):
    if file.endswith('.py'):
        route_name = file[:-3]
        root_module = import_module(f'routes.{route_name}')
        module = import_module(f'routes')
        globals()[route_name] = getattr(module, route_name)
        routes_list.append(root_module)

app = FastAPI(title="RegexTrainer", summary="", version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for thing in routes_list:
    app.include_router(thing.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("./static/favicon.png")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return """
    <html>
    <head>
        <title>RegexTrainer</title>
        <link rel="icon" type="image/png" href="/favicon.ico">
    </head>
    <body>
        <h1>RegexTrainer</h1>
        <p>Welcome to RegexTrainer! This is the backend API for the RegexTrainer application </p>
    </body>
    </html>
    """
    # return FileResponse(os.path.join("./react/dist", "index.html"))

@app.get("/status", status_code=status.HTTP_200_OK)
async def status():
    return {"status": "ok", "time": datetime.datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )