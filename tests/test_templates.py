import re, pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from html import escape
from app import app
from dotenv import load_dotenv

load_dotenv()

# Test client
client = TestClient(app)

# Const
TITLE = "<title>password, please!</title>"
STYLES = 'link href="http://testserver/static/styles.css" rel="stylesheet"'
SCRIPT = 'script src="http://testserver/static/script.js"'
REGEN_BUTTON = 'button id="regenerate-button"'
FOOTER = ('class="footer-link"', 'class="footer-logo"', "DevArno")

# Mock data
mock_password_map = {
    "diceware": "meteor-cactus-emerald-breeze-whistle-puzzle-antelope-whirlpool-nugget-gumdrop-vintage",
    "random": r"r8$\@!=Ae-/AQwC\sf:+RfbRZ+e[RYO%E(6^LltBF,&>,WIEbUx%\ea?v<BL*qJ6J2WA05jxxkgNVE{q",
    "argon2": "$argon2id$v=19$m=65536,t=3,p=4$DAMb8LHVZ1Uf6J/3G6NdKA$1mifCEFzlHHynI4Gl0QOvfpMaY",
    "uuid": "0897329f-de4d-4dfb-980a-d42dcac06f7e",
    "hash": "a1a37f050cbdb38bcbb04178559931e1b128c48ad89781f95f1ebac23d0adf79",
    "bcrypt": "$2b$12$PtkFCZTKd7gcDyjzVl8/a.Ion3.i.G1Rg9BEWotHjx1iU06D1rO22",
}

# Dependency injectors
def mock_generate_passwords():
    return mock_password_map

# Single password test helper
def run_password_test(password_type: str, mock_func):
    with patch(f"app.generator._create_{password_type}_password", side_effect=mock_func):
        response = client.get(f"/{password_type}")
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
def test_render_hash_password():
    run_password_test("hash", lambda: mock_password_map["hash"])

# Argon2 password test
def test_render_argon2_password():
    run_password_test("argon2", lambda: mock_password_map["argon2"])

# Bcrypt password test
def test_render_bcrypt_password():
    run_password_test("bcrypt", lambda: mock_password_map["bcrypt"])

# Random password test
def test_render_random_password():
    run_password_test("random", lambda: mock_password_map["random"])

# Diceware password test
def test_render_diceware_password():
    run_password_test("diceware", lambda: mock_password_map["diceware"])

# UUID password test
def test_render_uuid_password():
    run_password_test("uuid", lambda: mock_password_map["uuid"])
    
# Combined passwords test
@patch("app.generator._generate_all_passwords", side_effect=mock_generate_passwords)
def test_render_all_passwords(_):

    # Hit default route and extract response
    response = client.get("/")
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