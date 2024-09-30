import pytest
from unittest.mock import patch, mock_open
from generator import PasswordGenerator, PasswordType  # replace 'my_module' with your actual module name
import re
from argon2 import PasswordHasher

@pytest.fixture
def password_generator():
    return PasswordGenerator()

@pytest.fixture(autouse=True)
def mock_word_file():
    with patch("builtins.open", mock_open(read_data="word1\nword2\nword3")):
        yield

def test_create_random_password_length(password_generator):
    length = 80
    password = password_generator._create_random_password(length)
    assert len(password) == length

def test_create_random_password_complexity(password_generator):
    password = password_generator._create_random_password(password_generator.MIN_LENGTH)
    charsets = password_generator._charsets
    assert any(c in password for c in charsets[0])  # Lowercase
    assert any(c in password for c in charsets[1])  # Uppercase
    assert any(c in password for c in charsets[2])  # Digits
    assert any(c in password for c in charsets[3])  # Punctuation

def test_uuid_based(password_generator):
    uuid_password = password_generator.uuid_based()
    assert re.match(r'[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}', uuid_password)

def test_hash_based(password_generator):
    hash_password = password_generator.hash_based()
    assert len(hash_password) == 64  # SHA-256 produces a 64 character hex digest

def test_bcrypt_based(password_generator):
    bcrypt_password = password_generator.bcrypt_based()
    assert bcrypt_password.startswith('$2b$')

def test_argon2_based(password_generator):
    length = 80
    argon2_password = password_generator.argon2_based(length)
    assert len(argon2_password) >= 80
    assert argon2_password.startswith('$argon2')

def test_diceware_based_length(password_generator):
    length = 80
    diceware_password = password_generator.diceware_based(length)
    words = diceware_password.split('-')
    assert all(word in ["word1", "word2", "word3"] for word in words)

def test_diceware_based_words(password_generator):
    length = 80
    diceware_password = password_generator.diceware_based(length)
    words = diceware_password.split('-')
    assert all(word in ["word1", "word2", "word3"] for word in words)

def test_all_passwords_generated(password_generator):
    passwords = password_generator._generate_all_passwords()
    assert PasswordType.RANDOM.value in passwords
    assert PasswordType.ARGON2.value in passwords
    assert PasswordType.DICE.value in passwords
    assert PasswordType.UUID.value in passwords
    assert PasswordType.HASH.value in passwords
    assert PasswordType.BCRYPT.value in passwords

if __name__ == "__main__":
    pytest.main()