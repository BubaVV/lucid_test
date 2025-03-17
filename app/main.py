from fastapi import FastAPI
import uvicorn

import models
from resources import posts, auth

app = FastAPI()

app.include_router(posts)
app.include_router(auth)

@app.get("/healthcheck")
async def healtcheck():
    return "OK"


if __name__ == '__main__':
    models.init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
