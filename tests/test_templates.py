import re, pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app
from html import escape

# Test client
client = TestClient(app)

# Const
TITLE = "<title>password, please!</title>"
STYLES = 'link href="http://testserver/static/styles.css" rel="stylesheet"'
SCRIPT = 'script src="http://testserver/static/script.js"'
REGEN_BUTTON = 'button id="regenerate-button"'


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

def mock_create_hash_password():
    return mock_password_map["hash"]

def mock_create_argon2_password():
    return mock_password_map["argon2"]

def mock_create_bcrypt_password():
    return mock_password_map["bcrypt"]

def mock_create_uuid_password():
    return mock_password_map["uuid"]

def mock_create_diceware_password():
    return mock_password_map["diceware"]

def mock_create_random_password():
    return mock_password_map["random"]


# All passwords
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

def single_password_template_title(password_type: str):
    return f'<h1>🔐 Your <span style="color: orange">{password_type}</span> password</h1>'

# HASH
@patch("app.generator._create_hash_password", side_effect=mock_create_hash_password)
def test_render_hash_password(_):
    response = client.get("/hash")
    html_content = response.text
    assert response.status_code == 200
    assert TITLE in html_content
    header = single_password_template_title("hash")
    assert header in html_content
    escaped_password = escape(mock_password_map["hash"])
    password_regex = f'value="{re.escape(escaped_password)}"'
    assert re.search(password_regex, html_content) is not None, f"No hash password found"

# ARGON2
@patch("app.generator._create_argon2_password", side_effect=mock_create_argon2_password)
def test_render_argon2_password(_):
    response = client.get("/argon2")
    html_content = response.text
    assert response.status_code == 200
    assert TITLE in html_content
    header = single_password_template_title("argon2")
    assert header in html_content
    escaped_password = escape(mock_password_map["argon2"])
    password_regex = f'value="{re.escape(escaped_password)}"'
    assert re.search(password_regex, html_content) is not None, f"No argon2 password found"

# BCRYPT
@patch("app.generator._create_bcrypt_password", side_effect=mock_create_bcrypt_password)
def test_render_bcrypt_password(_):
    response = client.get("/bcrypt")
    html_content = response.text
    assert response.status_code == 200
    assert TITLE in html_content
    header = single_password_template_title("bcrypt")
    assert header in html_content
    escaped_password = escape(mock_password_map["bcrypt"])
    password_regex = f'value="{re.escape(escaped_password)}"'
    assert re.search(password_regex, html_content) is not None, f"No bcrypt password found"

# RANDOM
@patch("app.generator._create_random_password", side_effect=mock_create_random_password)
def test_render_random_password(_):
    response = client.get("/random")
    html_content = response.text
    assert response.status_code == 200
    assert TITLE in html_content
    header = single_password_template_title("random")
    assert header in html_content
    escaped_password = escape(mock_password_map["random"])
    password_regex = f'value="{re.escape(escaped_password)}"'
    assert re.search(password_regex, html_content) is not None, f"No random password found"
    
# DICEWARE
@patch("app.generator._create_diceware_password", side_effect=mock_create_diceware_password)
def test_render_diceware_password(_):
    response = client.get("/diceware")
    html_content = response.text
    assert response.status_code == 200
    assert TITLE in html_content
    header = single_password_template_title("diceware")
    assert header in html_content
    escaped_password = escape(mock_password_map["diceware"])
    password_regex = f'value="{re.escape(escaped_password)}"'
    assert re.search(password_regex, html_content) is not None, f"No diceware password found"
    
# UUID
@patch("app.generator._create_uuid_password", side_effect=mock_create_uuid_password)
def test_render_uuid_password(_):
    response = client.get("/uuid")
    html_content = response.text
    assert response.status_code == 200
    assert TITLE in html_content
    header = single_password_template_title("uuid")
    assert header in html_content
    escaped_password = escape(mock_password_map["uuid"])
    password_regex = f'value="{re.escape(escaped_password)}"'
    assert re.search(password_regex, html_content) is not None, f"No uuid password found"
    
if __name__ == "__main__":
    pytest.main()