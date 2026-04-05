import pytest

# Tests marked as e2e in case you only want to run them (i.e. pytest -m e2e)

@pytest.mark.e2e
def test_hello_world_e2e(page, fastapi_server):

    # Test that the homepage displays "Hello World" at the top

    page.goto('http://localhost:8000')

    assert page.inner_text('h1') == 'Hello World'

@pytest.mark.e2e
def test_add_e2e(page, fastapi_server):

    # Test that the add operation works in the browser

    # Go to homepage
    page.goto('http://localhost:8000')

    # Set the first and second numers and click the operation
    page.fill('#a', '10')
    page.fill('#b', '2')
    page.click('button:text("Add")')

    # Check that the result in the result div is correct
    assert page.inner_text('#result') == 'Calculation Result: 12'

@pytest.mark.e2e
def test_subtract_e2e(page, fastapi_server):

    # Test that the subtract operation works in the browser

    # Go to homepage
    page.goto('http://localhost:8000')

    # Set the first and second numers and click the operation
    page.fill('#a', '10')
    page.fill('#b', '2')
    page.click('button:text("Subtract")')

    # Check that the result in the result div is correct
    assert page.inner_text('#result') == 'Calculation Result: 8'

@pytest.mark.e2e
def test_multiply_e2e(page, fastapi_server):

    # Test that the multiply operation works in the browser

    # Go to homepage
    page.goto('http://localhost:8000')

    # Set the first and second numers and click the operation
    page.fill('#a', '10')
    page.fill('#b', '2')
    page.click('button:text("Multiply")')

    # Check that the result in the result div is correct
    assert page.inner_text('#result') == 'Calculation Result: 20'

@pytest.mark.e2e
def test_divide_e2e(page, fastapi_server):

    # Test that the divide operation works in the browser

    # Go to homepage
    page.goto('http://localhost:8000')

    # Set the first and second numers and click the operation
    page.fill('#a', '10')
    page.fill('#b', '2')
    page.click('button:text("Divide")')

    # Check that the result in the result div is correct
    assert page.inner_text('#result') == 'Calculation Result: 5'

@pytest.mark.e2e
def test_divide_by_zero_e2e(page, fastapi_server):

    # Test that the divide operation throws an error when b is zero in the browser

    # Go to homepage
    page.goto('http://localhost:8000')

    # Set the first and second numers and click the operation
    page.fill('#a', '10')
    page.fill('#b', '0')
    page.click('button:text("Divide")')

    # Check that the result in the result div is correct
    assert page.inner_text('#result') == 'Error: Cannot divide by zero!'
