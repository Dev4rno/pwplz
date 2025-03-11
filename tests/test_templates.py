import re
import pytest
from html import escape
from core.generator import PasswordType
from unittest.mock import patch
from core.env import env_handler
from main import limiter

# Const
TITLE = "<title>Password, Please! - Free Secure Password Generator</title>"
STYLES = 'link href="http://testserver/static/styles.css" rel="stylesheet"'
SCRIPT = 'script src="http://testserver/static/script.js"'
REGEN_BUTTON = 'button id="regenerate-button"'
FOOTER = ('class="footer-link"', 'class="footer-logo"', "DevArno")

# Mock data
mock_password_map = env_handler.mock_passwords
        
@pytest.fixture
def disable_limit():
    limiter.enabled = False
    yield limiter
        
# Single password test helper
def run_password_test(password_type: str, mock_func, test_client):
    with patch(f"main.generator._create_{password_type}_password", side_effect=mock_func):
        response = test_client.get(f"/{password_type}")
        html_content = response.text
        assert response.status_code == 200
        assert TITLE in html_content
        header = f'<h1>🔐 Your <span style="color: orange">{password_type}</span> password</h1>'
        assert header in html_content
        escaped_password = escape(mock_password_map[password_type])
        password_regex = f'value="{re.escape(escaped_password)}"'
        assert re.search(password_regex, html_content) is not None, f"No {password_type} password found"
        assert all(x in html_content for x in FOOTER)

# Hash password test
def test_render_hash_password(disable_limit, test_client):
    pwt = PasswordType.HASH.value
    run_password_test(pwt, lambda: mock_password_map[pwt], test_client)

# Argon2 password test
def test_render_argon2_password(disable_limit, test_client):
    pwt = PasswordType.ARGON2.value
    run_password_test(pwt, lambda: mock_password_map[pwt], test_client)

# Bcrypt password test
def test_render_bcrypt_password(disable_limit, test_client):
    pwt = PasswordType.BCRYPT.value
    run_password_test(pwt, lambda: mock_password_map[pwt], test_client)

# Random password test
def test_render_random_password(disable_limit, test_client):
    pwt = PasswordType.RANDOM.value
    run_password_test(pwt, lambda: mock_password_map[pwt], test_client)

# Diceware password test
def test_render_diceware_password(disable_limit, test_client):
    pwt = PasswordType.DICEWARE.value
    run_password_test(pwt, lambda: mock_password_map[pwt], test_client)

# UUID password test
def test_render_uuid_password(disable_limit, test_client):
    pwt = PasswordType.UUID.value
    run_password_test(pwt, lambda: mock_password_map[pwt], test_client)

# Combined passwords test
@patch("main.generator._generate_all_passwords", side_effect=lambda: mock_password_map)
def test_render_all_passwords(_, disable_limit, test_client):

    # Hit default route and extract response
    response = test_client.get("/")
    html_content = response.text
    
    # Assert expected properties
    assert response.status_code == 200
    assert TITLE in html_content
    assert '<h1>🔐 Passwords</h1>' in html_content

    # Verify each password
    for i, (method, password) in enumerate(mock_password_map.items()):

        # Method
        assert f'<span class="password-label">{method}</span>' in html_content

        # Password
        escaped_password = escape(password)
        password_regex = f'value="{re.escape(escaped_password)}"'
        assert re.search(password_regex, html_content) is not None, f"No password found for [{method}]"

        # Copy button
        copy_button_html = f'<button class="copy-button" onclick="copyToClipboard(\'password_{i+1}\', \'{method}\')">'
        assert copy_button_html in html_content

    # Check for additional template elements
    assert REGEN_BUTTON in html_content
    assert SCRIPT in html_content
    assert STYLES in html_content
    assert all(x in html_content for x in FOOTER)


if __name__ == "__main__":
    pytest.main()