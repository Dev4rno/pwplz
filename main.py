import os
import uvicorn
from core.app import app 

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)