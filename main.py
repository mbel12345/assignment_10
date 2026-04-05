'''
Create the FastAPI calculator application.
All API endpoints stored in app.routes so that they can be in the coverage report of the testing.
'''

import logging
import uvicorn

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes import CalculatorRouter

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI()

# Add Calculator Router to the app, for the operation endpoints
calc_router = CalculatorRouter(logger)
app.include_router(calc_router.router)

# Custom Exception handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, errors: HTTPException):

    logger.error(f'HTTPException on {request.url.path}: {errors.detail}')
    return JSONResponse(
        status_code=errors.status_code,
        content={'error': errors.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, errors: RequestValidationError):

    # Extract error messages
    error_messages = '; '.join([f'{err["loc"][-1]}: {err["msg"]}' for err in errors.errors()])
    logger.error(f'ValidationError on {request.url.path}: {error_messages}')
    return JSONResponse(
        status_code=400,
        content={'error': error_messages},
    )

if __name__ == '__main__':

    uvicorn.run(app, host='127.0.0.1', port=8000)
