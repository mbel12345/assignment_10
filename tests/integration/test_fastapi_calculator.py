import pytest

from fastapi.testclient import TestClient

from main import app

@pytest.fixture
def client():

    # Create a TestClient for the FastAPI application

    with TestClient(app) as client:
        yield client

def test_read_root(client):

    # Test that read_root returns a webpage

    # Do the API call
    response = client.get('/')

    # Check that the return code is 200 (OK)
    assert response.status_code == 200, f'Expected status code 200, got {response.status_code}'

    # Check that content-type is text/html
    assert 'text/html' in response.headers['content-type']

def test_add_api(client):

    # Test the add endpoint, and make it sure it returns the proper response.

    # Do the API call
    response = client.post('/add', json={'a': 10, 'b': 2})

    # Check that the return code is 200 (OK)
    assert response.status_code == 200, f'Expected status code 200, got {response.status_code}'

    # Check that the 'result' value in the response is correct
    actual = response.json()['result']
    expected = 12
    assert actual == expected, f'Expected result {expected}, got {actual}'

def test_subtract_api(client):

    # Test the subtract endpoint, and make it sure it returns the proper response.

    # Do the API call
    response = client.post('/subtract', json={'a': 10, 'b': 2})

    # Check that the return code is 200 (OK)
    assert response.status_code == 200, f'Expected status code 200, got {response.status_code}'

    # Check that the 'result' value in the response is correct
    actual = response.json()['result']
    expected = 8
    assert actual == expected, f'Expected result {expected}, got {actual}'

def test_multiply_api(client):

    # Test the multiply endpoint, and make it sure it returns the proper response.

    # Do the API call
    response = client.post('/multiply', json={'a': 10, 'b': 2})

    # Check that the return code is 200 (OK)
    assert response.status_code == 200, f'Expected status code 200, got {response.status_code}'

    # Check that the 'result' value in the response is correct
    actual = response.json()['result']
    expected = 20
    assert actual == expected, f'Expected result {expected}, got {actual}'

def test_divide_api(client):

    # Test the divide endpoint, and make it sure it returns the proper response.

    # Do the API call
    response = client.post('/divide', json={'a': 10, 'b': 2})

    # Check that the return code is 200 (OK)
    assert response.status_code == 200, f'Expected status code 200, got {response.status_code}'

    # Check that the 'result' value in the response is correct
    actual = response.json()['result']
    expected = 5
    assert actual == expected, f'Expected result {expected}, got {actual}'

def test_divide_by_zero_api(client):

    # Test that the divide endpoint throws an error when division by 0 is attempted

    # Do the API call
    response = client.post('/divide', json={'a': 10, 'b': 0})

    # Check that the return code is 400 (Bad Request)
    assert response.status_code == 400, f'Expected status code 400, got {response.status_code}'

    # Check that the JSON response contains an 'error' field
    assert 'error' in response.json(), "Response JSON does not contain 'error' field"

    # Check that the 'error' field contains the correct error message
    assert 'Cannot divide by zero!' in response.json()['error'], \
        f"Expected error message 'Cannot divide by zero!', got '{response.json()['error']}'"

def test_invalid_numbers(client):

    # Test that the add endpoint throws an error when invalid numbers are passed

    # Do the API call
    response = client.post('/add', json={'a': 10, 'b': 'abc'})

    # Check that the return code is 400 (Bad Request)
    assert response.status_code == 400, f'Expected status code 400, got {response.status_code}'

    # Check that the JSON response contains an 'error' field
    assert 'error' in response.json(), "Response JSON does not contain 'error' field"

    expected = 'Both a and b must be numbers.'
    # Check that the 'error' field contains the correct error message
    assert expected in response.json()['error'], \
        f"Expected error message '{expected}', got '{response.json()['error']}'"

def test_add_generic_failure(client, monkeypatch):

    # Force failure in add operation, to make sure the error handling works for generic/uncategorized failures

    def force_fail(a, b):
        raise RuntimeError('Force failure')

    monkeypatch.setattr('app.routes.add', force_fail)

    response = client.post('/add', json={'a': 10, 'b': 2})

    assert response.status_code == 400
    assert 'Force failure' in response.json()['error']

def test_subtract_generic_failure(client, monkeypatch):

    # Force failure in subtract operation, to make sure the error handling works for generic/uncategorized failures

    def force_fail(a, b):
        raise RuntimeError('Force failure')

    monkeypatch.setattr('app.routes.subtract', force_fail)

    response = client.post('/subtract', json={'a': 10, 'b': 2})

    assert response.status_code == 400
    assert 'Force failure' in response.json()['error']

def test_multiply_generic_failure(client, monkeypatch):

    # Force failure in multiply operation, to make sure the error handling works for generic/uncategorized failures

    def force_fail(a, b):
        raise RuntimeError('Force failure')

    monkeypatch.setattr('app.routes.multiply', force_fail)

    response = client.post('/multiply', json={'a': 10, 'b': 2})

    assert response.status_code == 400
    assert 'Force failure' in response.json()['error']

def test_divide_generic_failure(client, monkeypatch):

    # Force failure in divide operation, to make sure the error handling works for generic/uncategorized failures

    def force_fail(a, b):
        raise RuntimeError('Force failure')

    monkeypatch.setattr('app.routes.divide', force_fail)

    response = client.post('/divide', json={'a': 10, 'b': 2})

    assert response.status_code == 400
    assert 'Force failure' in response.json()['error']
