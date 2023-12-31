from collections.abc import Callable

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from core.exceptions import CoreException, ErrorDetail, ErrorLink, ErrorResponse

from .api.v1.router import initializeRouter

app = FastAPI()


class DTOPROCESSOR(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        print("get init", original_route_handler)

        async def custom_route_handler(request: Request) -> Response:
            response = await original_route_handler(request)
            print("RESS aaa", response)
            return response

        return custom_route_handler


@app.exception_handler(CoreException)
async def core_exception_handler(request: Request, exc: CoreException):
    error_link = exc.links
    if error_link is None:
        error_link = ErrorLink(about="Not available", error_type="Undocumented")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status=exc.status_code,
            detail=ErrorDetail(
                title="No title" if exc.title is None else exc.title,
                message=exc.message,
            ),
            links=error_link,
        ).dict(),
    )


initializeRouter(app)

app.router.route_class = DTOPROCESSOR
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return "hello"


def main():
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
