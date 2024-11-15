from argon2 import PasswordHasher
from enum import Enum
import random
from typing import Dict, List
import string, secrets, itertools, uuid, hashlib, bcrypt
import base64

########################>
class PasswordType(Enum):
########################>
    RANDOM="random"
    ARGON2="argon2"
    DICEWARE="diceware"
    UUID="uuid"
    HASH="hash"
    BCRYPT="bcrypt"

########################>
class PasswordGenerator:
########################>
    
    def __init__(self, **kwargs):
        if not all([x in ("min_length", "words") for x in kwargs]):
            raise ValueError("Invalid PasswordGenerator initialisation")
        self.min_length = kwargs["min_length"]
        self.words = kwargs["words"]
        self.charsets = [
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.digits,
            string.punctuation,
        ]

    #-=-=-=-=-=-=-=-=-=->

    def _create_random_password(self) -> str:
        """Generate a password using random sampling"""
        password_chars = [secrets.choice(charset) for charset in self.charsets]
        permitted_chars = ''.join(itertools.chain(*self.charsets))
        chars_left = self.min_length - len(password_chars)
        for _ in range(chars_left):        
            password_chars += [secrets.choice(permitted_chars)]
        secrets.SystemRandom().shuffle(password_chars) 
        password = ''.join(password_chars) 
        return password

    #-=-=-=-=-=-=-=-=-=->

    def _create_uuid_password(self) -> uuid.UUID:
        """Generate a Universally Unique Identifier password"""
        return str(uuid.uuid4())

    #-=-=-=-=-=-=-=-=-=->

    def _create_hash_password(self) -> str:
        """Generate a password using a hash function"""
        random_string = secrets.token_bytes(16) # Random byte string
        hash_digest = hashlib.sha256(random_string).hexdigest()  # Hash byte string
        return hash_digest

    #-=-=-=-=-=-=-=-=-=->

    def _create_bcrypt_password(self) -> str:
        """Generate a bcrypt salted / hashed password"""
        # Generate random salt
        salt = bcrypt.gensalt() 
        # Hash 16 random bytes with salt
        password = bcrypt.hashpw(secrets.token_bytes(16), salt)
        # Decode the password from bytes to a UTF-8 string, ignoring any errors
        password = password.decode("utf-8", "ignore")       
        return password

    #-=-=-=-=-=-=-=-=-=->

    def _create_argon2_password(self) -> str:
        """Generate a password using Argon2"""
        hasher = PasswordHasher()
        password = hasher.hash(secrets.token_hex(32))
        return password[:self.min_length] 

    #-=-=-=-=-=-=-=-=-=->

    def _create_diceware_password(self) -> str:
        """Generate a Diceware-based password"""
        password = ""
        wordlist = self._get_random_words()
        if not wordlist:
            return ""        
        # Append words min_length is met
        while len(password) < self.min_length:
            word = secrets.choice(wordlist)
            if password:
                password += '-'
            password += word
        
        return password

    #-=-=-=-=-=-=-=-=-=->

    def _get_password_creation_method(self, password_type: PasswordType):
        """Fetches the corresponding password creation method based on password type."""
        password_types = (item.value for item in PasswordType)
        exists = password_type.value in password_types if not isinstance(password_type, str) else password_type in password_types
        if not exists:
            raise ValueError(f"No method found for {password_type}")
        return getattr(self, f"_create_{password_type.value if not isinstance(password_type, str) else password_type}_password")

    #-=-=-=-=-=-=-=-=-=->

    def _generate_all_passwords(self) -> Dict[str, str]:
        """Generates passwords for all types defined in PasswordType."""
        passwords = {}
        for password_type in PasswordType:
            method = self._get_password_creation_method(password_type)
            passwords[password_type.value] = method()
        return passwords
    
    #-=-=-=-=-=-=-=-=-=->

    def _get_random_words(self) -> List[str]:
        """Retrieve individual words from the DICEWARE_WORDS env variable"""
        words = self.words.split('-')
        return [word.strip() for word in words if word.strip()]
    
    #-=-=-=-=-=-=-=-=-=->

    def _get_random_password_type(self):
        return random.choice(list(PasswordType)).value
