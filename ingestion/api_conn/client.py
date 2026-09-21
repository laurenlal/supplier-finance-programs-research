import os
from pathlib import Path

import calcbench as cb 
from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_FILE)


def initialize_calcbench():

    username = os.getenv("CALCBENCH_USERNAME") or os.getenv("CALCBENCH_USER")
    password = os.getenv("CALCBENCH_PASSWORD")

    if not username or not password:
        raise EnvironmentError(
            "Missing Calcbench credentials. "
            "Set CALCBENCH_USERNAME and CALCBENCH_PASSWORD "
            "in your environment or .env file."
        )

    # Explicitly set credentials so the behavior is predictable
    cb.set_credentials(username, password)

    # Retry failed requests using exponential backoff
    cb.enable_backoff()

    return cb
