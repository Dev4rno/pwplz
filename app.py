import os 
from flask import Flask, render_template
from generator import PasswordGenerator

# Initialise
app = Flask(__name__)
generator = PasswordGenerator()

# Default route
@app.route('/')
def home():
    """Generate passwords and render them in a simple HTML page."""
    passwords = generator._generate_all_passwords()
    return render_template('index.html', passwords=passwords)

# Default script
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))