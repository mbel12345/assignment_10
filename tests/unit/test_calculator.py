import pytest

from app.operations import add
from app.operations import divide
from app.operations import multiply
from app.operations import subtract

class BaseOperationTest:

    '''
    Use this class to facilitate paramterized testing, instead of the lengthy pytest.mark.parametrize.
    This also means testing will be standardized across different sub-classes.
    '''

    def test_valid_operations(self):

        # Test operation with valid inputs

        for name, case in self.valid_test_cases.items():
            a = case['a']
            b = case['b']
            expected = case['expected']
            actual = self.operation(a, b)
            assert actual == expected, f'Failed case: {name}'

    def test_invalid_operations(self):

        # Test operation with invalid inputs, and verify the correct errors were raised.

        for _, case in self.invalid_test_cases.items():
            a = case['a']
            b = case['b']
            expected_error = case['error']
            expected_message = case['message']
            with pytest.raises(expected_error, match=expected_message):
                self.operation(a, b)

class TestAdditionOperation(BaseOperationTest):

    '''
    Test Addition operation
    '''

    operation = staticmethod(lambda a, b: add(a, b))
    valid_test_cases = {
        'positive_numbers': {'a': 5, 'b': 3, 'expected': 8},
        'negative_numbers': {'a': -5, 'b': -3, 'expected': -8},
        'mixed_signs': {'a': -5, 'b': 3, 'expected': -2},
        'zero_sum': {'a': 5, 'b': -5, 'expected': 0},
        'decimals': {'a': 5.5, 'b': 3.3, 'expected': 8.8},
    }
    invalid_test_cases = {}

class TestSubtractionOperation(BaseOperationTest):

    '''
    Test Subtraction operation
    '''

    operation = staticmethod(lambda a, b: subtract(a, b))
    valid_test_cases = {
        'positive_numbers': {'a': 5, 'b': 3, 'expected': 2},
        'negative_numbers': {'a': -5, 'b': -3, 'expected': -2},
        'mixed_signs': {'a': -5, 'b': 3, 'expected': -8},
        'zero_result': {'a': 5, 'b': 5, 'expected': 0},
        'decimals': {'a': 5.5, 'b': 3.3, 'expected': 2.2},
    }
    invalid_test_cases = {}

class TestMultiplicationOperation(BaseOperationTest):

    '''
    Test Multiplication operation
    '''

    operation = staticmethod(lambda a, b: multiply(a, b))
    valid_test_cases = {
        'positive_numbers': {'a': 5, 'b': 3, 'expected': 15},
        'negative_numbers': {'a': -5, 'b': -3, 'expected': 15},
        'mixed_signs': {'a': -5, 'b': 3, 'expected': -15},
        'multiply_by_zero': {'a': 5, 'b': 0, 'expected': 0},
        'decimals': {'a': 5.5, 'b': 3.3, 'expected': 18.15},
    }
    invalid_test_cases = {}

class TestDivisionOperation(BaseOperationTest):

    '''
    Test Division operation
    '''

    operation = staticmethod(lambda a, b: divide(a, b))
    valid_test_cases = {
        'positive_numbers': {'a': 6, 'b': 2, 'expected': 3},
        'negative_numbers': {'a': -6, 'b': -2, 'expected': 3},
        'mixed_signs': {'a': -6, 'b': 2, 'expected': -3},
        'decimals': {'a': 5.5, 'b': 2, 'expected': 2.75},
        'divide_zero_numerator': {'a': 0, 'b': 5, 'expected': 0},
    }
    invalid_test_cases = {
        'divide_by_zero': {'a': 5, 'b': 0, 'error': ValueError, 'message': 'Cannot divide by zero!'},
    }
