import html
import re
import pytest
import time

from fastapi import status, HTTPException
from core.generator import PasswordType
from core.env import env_handler
from core.strings import is_valid_warning

# Env
default_rate_limit = 5#env_handler.default_rate_limit
advanced_rate_limit = 10#env_handler.advanced_rate_limit

# Error label extractor
def get_error_text(html_block: str):
    regex_pattern = r'<div class="error-detail">(.*?)</div>'
    match = re.search(regex_pattern, html_block)
    return html.unescape(match.group(1).strip())

# Rate limit exception trigger function
def run_rate_limit_test(test_client, url: str, limit: int):

    # Iterate allowable number of requests
    for _ in range(limit):
        time.sleep(0.1)
        response = test_client.get(url)
        assert response.status_code == 200, f"Invalid status code: {response.status_code}"

    # Follow with rate-limit trigger request
    response = test_client.get(url)
    html_block = response.text
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS, f"Unexpected status code: {response.status_code}"
    
    # Verify error details
    warning_text = get_error_text(html_block)
    assert is_valid_warning(warning_text), f"Unexpected warning: {warning_text}"

# Default rate limit test
def test_default_rate_limit_exception_handler(test_client):
    run_rate_limit_test(test_client, "/", default_rate_limit)

# Advanced rate limit test
def test_advanced_rate_limit_exception_handler(test_client):
    run_rate_limit_test(test_client, "/" + PasswordType.random_type(), advanced_rate_limit)

# HTTPException handler test
def test_http_exception_handler(test_client):
    response = test_client.get("/not-a-real-endpoint")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Unexpected status: {response.status_code}"
    html_block = response.text
    assert '<div class="status-code">Whoops</div>' in html_block, 'Expected block with class="status-code"'
    assert '<div class="error-message">Something went wrong</div>' in html_block, 'Expected block with class="error-message"'

if __name__ == "__main__":
    pytest.main()