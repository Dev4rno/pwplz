import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.fixture
def mock_password_data():
    return {
        "diceware": "meteor-cactus-emerald-breeze-whistle-puzzle-antelope-whirlpool-nugget-gumdrop-vintage",
        "random": "wwM'mI3D2=12:)$d%,Pc&s,3wP@zU0Cyk,lOGUv0'?/j*2a]D0&XMR#?'OKcr@-M-R",  # Removed the escape character here
        "argon2": "$argon2id$v=19$m=65536,t=3,p=4$DAMb8LHVZ1Uf6J/3G6NdKA$1mifCEFzlHHynI4Gl0QOvfpMaY",
        "uuid": "0897329f-de4d-4dfb-980a-d42dcac06f7e",
        "hash": "a1a37f050cbdb38bcbb04178559931e1b128c48ad89781f95f1ebac23d0adf79",
        "bcrypt": "$2b$12$PtkFCZTKd7gcDyjzVl8/a.Ion3.i.G1Rg9BEWotHjx1iU06D1rO22",
    }

def mock_generate_passwords():
    return mock_password_data()  # This function is fine

@patch('app.generator._generate_all_passwords', side_effect=mock_generate_passwords)
def test_password_template_rendering(mock_generate_passwords, mock_password_data):
    # Make a request to the route, which should now use the mocked password data
    response = client.get("/")
    html_content = response.text

    # Check if the response was successful
    assert response.status_code == 200
    assert "<title>password, please!</title>" in html_content
    assert '<h1>Passwords</h1>' in html_content

    # Verify each password method and value
    for method, password in mock_password_data.items():
        assert f'<span class="password-label">{method}</span>' in html_content
        assert f'value="{password}"' in html_content  # Match the exact password value

    # Check for additional template elements
    assert 'id="regenerate-button"' in html_content
    assert 'src="/static/script.js"' in html_content
    assert 'href="/static/styles.css"' in html_content
