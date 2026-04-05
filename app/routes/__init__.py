'''
All API endpoints stored in app.routes so that they can be in the coverage report of the testing.
'''

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator

from app.operations import add
from app.operations import divide
from app.operations import multiply
from app.operations import subtract

# Pydantic model for requests
class OperationRequest(BaseModel):

    a: float = Field(..., description='First number')
    b: float = Field(..., description='Second number')

    @field_validator('a', 'b', mode='before') # Force this to happen before Pydantic tries to coerce the value
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError('Both a and b must be numbers.')
        return value

# Pydantic model for successful responses
class OperationResponse(BaseModel):

    result: float = Field(..., descrption='Result of the operation')

# Pydantic model for error responses
class ErrorResponse(BaseModel):

    error: str = Field(..., description='Error message')

# Main router for the application

class CalculatorRouter:

    def __init__(self, logger):

        self.router = APIRouter(prefix='')

        self.router.get('/')(self.read_root)
        self.router.post('/add', response_model=OperationResponse, responses={400: {'model': ErrorResponse}})(self.add)
        self.router.post('/subtract', response_model=OperationResponse, responses={400: {'model': ErrorResponse}})(self.subtract)
        self.router.post('/multiply', response_model=OperationResponse, responses={400: {'model': ErrorResponse}})(self.multiply)
        self.router.post('/divide', response_model=OperationResponse, responses={400: {'model': ErrorResponse}})(self.divide)

        self.logger = logger

    async def read_root(self, request: Request):

        # Define directory for HTML templates to render
        templates = Jinja2Templates(directory='templates')

        # Serve index.html
        return templates.TemplateResponse('index.html', {'request': request})

    async def add(self, operation: OperationRequest):

        # Add two numbers

        try:
            result = add(operation.a, operation.b)
            return OperationResponse(result=result)
        except Exception as e:
            self.logger.error(f'Add Operation Error: {str(e)}')
            raise HTTPException(status_code=400, detail=str(e))

    async def subtract(self, operation: OperationRequest):

        # Subtract two numbers

        try:
            result = subtract(operation.a, operation.b)
            return OperationResponse(result=result)
        except Exception as e:
            self.logger.error(f'Subtract Operation Error: {str(e)}')
            raise HTTPException(status_code=400, detail=str(e))

    async def multiply(self, operation: OperationRequest):

        # Mulitply two numbers

        try:
            result = multiply(operation.a, operation.b)
            return OperationResponse(result=result)
        except Exception as e:
            self.logger.error(f'Multiply Operation Error: {str(e)}')
            raise HTTPException(status_code=400, detail=str(e))

    async def divide(self, operation: OperationRequest):

        # Divide two numbers

        try:
            result = divide(operation.a, operation.b)
            return OperationResponse(result=result)
        except ValueError as e:
            self.logger.error(f'Divide Operation Error: {str(e)}')
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            self.logger.error(f'Divide Operation Error: {str(e)}')
            raise HTTPException(status_code=400, detail=str(e))
