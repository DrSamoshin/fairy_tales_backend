from app.main import main_app
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def generate_file():
    with open(f"{BASE_DIR}/temp_files/openapi.json", "w") as f:
        json.dump(main_app.openapi(), f, indent=2)


if __name__ == "__main__":
    generate_file()
