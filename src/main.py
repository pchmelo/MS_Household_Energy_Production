from json import load
import os
from dotenv import load_dotenv

load_dotenv()
mode = os.getenv("MODE")

print("Hello World!")