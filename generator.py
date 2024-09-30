from argon2 import PasswordHasher
from enum import Enum
from typing import Dict, List
import os, string, secrets, itertools, uuid, hashlib, bcrypt

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
class PasswordType(Enum):
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
    RANDOM="random"
    ARGON2="argon2"
    DICE="dice"
    UUID="uuid"
    HASH="hash"
    BCRYPT="bcrypt"
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
class PasswordGenerator:
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
    MIN_LENGTH = 80
    WORD_FILE = "words.txt"
    # > > > > > > > > >
    def __init__(self):
    # > > > > > > > > >
        self._words_filepath = os.path.join(os.getcwd(), self.WORD_FILE)
        self._charsets = [
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.digits,
            string.punctuation,
        ]
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
    # def _generate_all_passwords(self) -> Dict['PasswordType', str]:
    def _generate_all_passwords(self) -> Dict[PasswordType, str]:
    # > > > > > > > > >
        return {
            PasswordType.RANDOM.value: self._create_random_password(self.MIN_LENGTH),
            PasswordType.ARGON2.value: self.argon2_based(self.MIN_LENGTH),
            PasswordType.DICE.value: self.diceware_based(self.MIN_LENGTH),
            PasswordType.UUID.value: self.uuid_based(),
            PasswordType.HASH.value: self.hash_based(),
            PasswordType.BCRYPT.value: self.bcrypt_based(),
        }
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
    def _get_random_words(self) -> List[str]:
    # > > > > > > > > >
        words = []
        with open(self._words_filepath, 'r') as file:
            for line in file:
                words.append(line.strip())
        return words
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
    def _create_random_password(self, length) -> str:
        """Generate a password using random sampling"""
    # > > > > > > > > >
        password_chars = [secrets.choice(x) for x in self._charsets]
        permitted_chars = ''.join(itertools.chain(*self._charsets))
        password_chars += [secrets.choice(permitted_chars) for _ in range(length - len(password_chars))]
        secrets.SystemRandom().shuffle(password_chars) # Shuffle the list to avoid predictable patterns
        password = ''.join(password_chars) # Convert list to string and return
        return password
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
    def uuid_based(self) -> uuid.UUID:
        """Generate a password based on UUID"""
    # > > > > > > > > >
        return str(uuid.uuid4())
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
    def hash_based(self) -> str:
        """Generate a password using a hash function"""
    # > > > > > > > > >
        random_string = secrets.token_bytes(16)  # Generate a random byte string
        hash_digest = hashlib.sha256(random_string).hexdigest()  # Hash the byte string
        return hash_digest
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
    def bcrypt_based(self) -> str:
        """Generate a password using bcrypt for hashing"""
    # > > > > > > > > >
        salt = bcrypt.gensalt()
        password = bcrypt.hashpw(secrets.token_bytes(16), salt)
        password = password.decode('utf-8', 'ignore')
        return password
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
    def argon2_based(self, length) -> str:
        """Generate a password using Argon2"""
    # > > > > > > > > >
        ph = PasswordHasher()
        password = ph.hash(secrets.token_hex(32))
        return password[:length] 
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=->
    def diceware_based(self, length) -> str:
        """Generate a passphrase using the Diceware method"""
    # > > > > > > > > >
        password = ""
        wordlist = self._get_random_words()
        while len(password) < length:
            password += secrets.choice(wordlist) + '-'
        return password.rstrip('-')

