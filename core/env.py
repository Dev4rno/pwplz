import os
from typing import Any, Optional
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=dotenv_path)

# Centralized env handler
class EnvHandler:
    
    def __init__(self):
        """Add new variables below"""
        self.words = self.get("DICEWARE_WORDS")
        self.min_length = self.get("MIN_LENGTH", None, int)
        self.analytics_key = self.get("API_ANALYTICS_KEY")
        self.default_rate_limit = self.get("DEFAULT_RATE_LIMIT", None, int)
        self.advanced_rate_limit = self.get("ADVANCED_RATE_LIMIT", None, int)
        self.mock_passwords = {
            "diceware": "meteor-cactus-emerald-breeze-whistle-puzzle-antelope-whirlpool-nugget-gumdrop-vintage",
            "random": r"r8$\@!=Ae-/AQwC\sf:+RfbRZ+e[RYO%E(6^LltBF,&>,WIEbUx%\ea?v<BL*qJ6J2WA05jxxkgNVE{q",
            "argon2": "$argon2id$v=19$m=65536,t=3,p=4$DAMb8LHVZ1Uf6J/3G6NdKA$1mifCEFzlHHynI4Gl0QOvfpMaY",
            "uuid": "0897329f-de4d-4dfb-980a-d42dcac06f7e",
            "hash": "a1a37f050cbdb38bcbb04178559931e1b128c48ad89781f95f1ebac23d0adf79",
            "bcrypt": "$2b$12$PtkFCZTKd7gcDyjzVl8/a.Ion3.i.G1Rg9BEWotHjx1iU06D1rO22",
        }

    def get(self, key: str, default: Optional[Any] = None, cast: Optional[type] = None) -> Any:
        """
        Fetch an environment variable with optional casting and default fallback.

        :param key: Name of the environment variable.
        :param default: Default value if the variable is not found.
        :param cast: Type to cast the value into (e.g., int, float, bool).
        :return: The value of the environment variable.
        :raises KeyError: If the variable is not found and no default is provided.
        """
        value = os.getenv(key, default)
        if value is None:
            raise KeyError(f"Missing required environment variable: {key}")
        
        if cast:
            try:
                value = cast(value)
            except ValueError as e:
                raise ValueError(f"Error casting environment variable {key} to {cast}: {e}")
        
        return value

# Instantiate for global use
env_handler = EnvHandler()