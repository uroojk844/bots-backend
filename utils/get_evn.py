import os
from dotenv import load_dotenv

load_dotenv()


def load_env(key: str, default: str = ""):
    value = os.environ.get(key, default)
    print(f"Using {key} = {value}")
    return value
