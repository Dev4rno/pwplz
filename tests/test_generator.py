import pytest
from unittest.mock import patch, mock_open
from generator import PasswordGenerator, PasswordType
import re, os

WORDS = "apple-bicycle-caterpillar-dragonfly-elephant-furniture-giraffe-horizon-iguana-jacket-kitchen-lighthouse-mountain-notebook-octopus-penguin-quasar-rainbow-sunflower-telescope-umbrella-vortex-window-xylophone-yacht-zebra-airplane-bookcase-cactus-dolphin-envelope-forest-guitar-honeycomb-iceberg-jungle-koala-lemonade-mushroom-neutron-orchestra-puzzle-quilt-robot-snowflake-train-unicorn-volcano-whale-xenon-yogurt-biscuit-carpet-dandelion-echo-flamingo-glasses-hammock-insect-jellyfish-kaleidoscope-laptop-maple-noodle-octagon-peacock-reindeer-snowman-trolley-vintage-whistle-zeppelin-airbag-bison-carousel-dome-frost-grape-incense-jigsaw-keyhole-lemur-moose-nebula-onion-plasma-radio-skateboard-tangerine-useless-vacuum-whirlpool-yarn-zinnia-acorn-balloon-chandelier-dinosaur-fossil-galaxy-hologram-ivory-jewel-kerchief-mosaic-obsidian-quiver-relic-sapphire-toothbrush-ultrasound-vortex-wand-abacus-bandana-cupcake-eggplant-grapefruit-honey-ink-kiosk-lemon-moonlight-nostalgia-rose-sunset-telephone-underwear-vulture-waffle-apron-breeze-drum-embroidery-fish-inbox-keychain-mango-neon-orange-quokka-ribbon-sandcastle-television-universe-vaccine-waterfall-antelope-beach-cloud-deck-fireplace-garden-hibiscus-icecream-jewelry-kettle-nightingale-oak-quill-rooster-skyscraper-violet-yellow-zoo-albatross-blueberry-dragon-emerald-feather-hibiscus-hotdog-igloo-jaguar-lantern-narwhal-opal-pancake-spiral-tricycle-vanilla-walrus-yeti-zookeeper-ballet-daffodil-eclipse-fiesta-gumdrop-harp-jagged-kale-lavender-marzipan-nutmeg-ostrich-parabola-quasar-rocket-starfish-turtle-willow-xerox-yoga-arrow-compass-evergreen-fiesta-inkblot-jagged-kale-lettuce-meteor-pluto-raspberry-tambourine-ukelele-violets-walnut-yoke-adventure-badge-comet-frog-helium-island-joker-knight-log-nugget-oyster-planet-shield"
MIN_LENGTH = 80

@pytest.fixture
def generator():
    return PasswordGenerator(MIN_LENGTH, WORDS)

@pytest.fixture(autouse=True)
def mock_word_file():
    with patch("builtins.open", mock_open(read_data="word1\nword2\nword3")):
        yield

#-=-=-=-=-=-=-=-=-=->

def test_create_random_password_length(generator):
    password = generator._create_random_password()
    assert len(password) == generator.min_length

#-=-=-=-=-=-=-=-=-=->

def test_create_random_password_complexity(generator):
    password = generator._create_random_password()
    charsets = generator.charsets
    assert any(c in password for c in charsets[0])  # Lowercase
    assert any(c in password for c in charsets[1])  # Uppercase
    assert any(c in password for c in charsets[2])  # Digits
    assert any(c in password for c in charsets[3])  # Punctuation

#-=-=-=-=-=-=-=-=-=->

def test_uuid_password(generator):
    uuid_password = generator._create_uuid_password()
    assert re.match(r'[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}', uuid_password)

#-=-=-=-=-=-=-=-=-=->

def test_hash_password(generator):
    hash_password = generator._create_hash_password()
    assert len(hash_password) == 64  # SHA-256 produces a 64 character hex digest

#-=-=-=-=-=-=-=-=-=->

def test_bcrypt_password(generator):
    bcrypt_password = generator._create_bcrypt_password()
    assert bcrypt_password.startswith('$2b$')

#-=-=-=-=-=-=-=-=-=->

def test_argon2_password(generator):
    argon2_password = generator._create_argon2_password()
    assert argon2_password.startswith('$argon2')
    assert len(argon2_password) >= generator.min_length

#-=-=-=-=-=-=-=-=-=->

def test_diceware_password(generator):
    diceware_password = generator._create_diceware_password()
    words = diceware_password.split('-')
    assert all(word in WORDS.split("-") for word in words)
    assert len(diceware_password) >= generator.min_length

#-=-=-=-=-=-=-=-=-=->

def test_all_passwords(generator):
    passwords = generator._generate_all_passwords()
    for password_type in PasswordType:
        assert password_type.value in passwords, f"Missing {password_type.value} password."

#-=-=-=-=-=-=-=-=-=->

def test_zero_min_length():
    generator = PasswordGenerator(0, WORDS)
    random_password = generator._create_random_password()
    assert len(random_password) == 4  # minimum complexity should produce 4 characters

#-=-=-=-=-=-=-=-=-=->

def test_minimum_length_of_one():
    generator = PasswordGenerator(1, WORDS)
    random_password = generator._create_random_password()
    assert len(random_password) == 4  # minimum complexity should produce 4 characters

#-=-=-=-=-=-=-=-=-=->

def test_diceware_with_empty_words():
    generator = PasswordGenerator(10, "")
    diceware_password = generator._create_diceware_password()
    print("DOCEWAREAFEWKMFAL:F", diceware_password)
    assert diceware_password == ""

#-=-=-=-=-=-=-=-=-=->

def test_random_password_type_selection(generator):
    password_type = generator._get_random_password_type()
    assert password_type in [ptype.value for ptype in PasswordType]

if __name__ == "__main__":
    pytest.main()