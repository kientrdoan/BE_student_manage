import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent


def load_env():
    is_override: bool = False
    get_env = os.environ.get("DJANGO_ENV", "") or os.environ.get("APP_ENV", "")
    if get_env:
        env_path = os.path.join(BASE_DIR, '.env.' + get_env.lower())
    else:
        is_override = True
        env_path = os.path.join(BASE_DIR, '.env.local')

    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path, override=is_override)
        sys.stdout.write(f"[Dotenv] Loading environment from `{env_path}`... ok \n")
    else:
        sys.stdout.write(f"[Dotenv] Loading environment from `{env_path}`... failed \n")
