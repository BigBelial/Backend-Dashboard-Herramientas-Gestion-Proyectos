from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from application.dtos.response_dto import ResponseDTO
from infrastructure.config.settings import settings
from infrastructure.database.mongodb import close_mongo_connection, connect_to_mongo
from presentation.api.v1.routes.auth import router as auth_router
from presentation.api.v1.routes.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseDTO(
            status_code=exc.status_code,
            message="Error",
            error=exc.detail,
        ).model_dump(),
    )


def _serialize_validation_errors(errors: list) -> list:
    result = []
    for err in errors:
        e = dict(err)
        if "ctx" in e:
            ctx = dict(e["ctx"])
            if isinstance(ctx.get("error"), Exception):
                ctx["error"] = str(ctx["error"])
            e["ctx"] = ctx
        result.append(e)
    return result


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ResponseDTO(
            status_code=422,
            message="Validation error",
            error=_serialize_validation_errors(exc.errors()),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ResponseDTO(
            status_code=500,
            message="Internal server error",
            error=str(exc),
        ).model_dump(),
    )


app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
