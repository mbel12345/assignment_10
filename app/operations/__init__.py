'''
Functions:
  - add(a: Number, b: Number): Return the sum of a and b
  - subtract(a: Number, b: Number): Retun the difference of a and b
  - multiple(a: Number, b: Number): Return the product of a and b
  - divide(a: Number, b: Number): Return the quotient of a and b. Raise ValueError if b is 0.

Usage:
  - These can be used in the calculator web app.
'''

from typing import Union

Number = Union[int, float] # All operation inputs and outputs should be ints or floats

def add(a: Number, b: Number) -> Number:

    '''
    Add a and b.

    Parameters:
      - a (Number): First number to add
      - b (Number): Second number to add

    Return:
      - Number: Sum of a and b

    Example:
    add(4, 4.5) = 8.5
    '''

    return a + b

def subtract(a: Number, b: Number) -> Number:

    '''
    Subtract a and b.

    Parameters:
      - a (Number): First number to subtract
      - b (Number): Second number to subtract

    Return:
      - Number: Difference of a and b

    Example:
    add(4, 4.5) = -0.5
    '''

    return a - b

def multiply(a: Number, b: Number) -> Number:

    '''
    Multiply a and b.

    Parameters:
      - a (Number): First number to multiply
      - b (Number): Second number to multiply

    Return:
      - Number: Product of a and b

    Example:
    add(4, 4.5) = 18
    '''

    return a * b

def divide(a: Number, b: Number) -> Number:

    '''
    Divide a and b.

    Parameters:
      - a (Number): First number to divide
      - b (Number): Second number to divide

    Return:
      - Number: Quotient of a and b
      - ValueError if b is 0

    Example:
    add(7.5, 2.5) = 3
    '''

    if b == 0:
        raise ValueError('Cannot divide by zero!')

    return a / b
