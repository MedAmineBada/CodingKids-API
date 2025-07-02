from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse

import routers.users as users

app = FastAPI()

app.include_router(users.router)


@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    return HTMLResponse(
        content="""
        <html><head><title>Page Not Found</title></head>
        <body><h1>404 – Page Not Found</h1>
               <p>We can't find what you're looking for.</p></body></html>
        """,
        status_code=404,
    )
