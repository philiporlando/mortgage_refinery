import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class SMTPConfig(BaseModel):
    host: str
    port: int = 587
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False


class EmailConfig(BaseModel):
    recipients: list[str] = Field(..., alias="to")


class ProfileConfig(BaseModel):
    threshold: float
    smtp: SMTPConfig
    email: EmailConfig


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml if it exists."""
    load_dotenv()
    deployment = os.environ.get("DEPLOYMENT", "development")
    data = yaml.safe_load(Path("config.yaml").read_text())
    profile = data.get("profiles", {}).get(deployment)
    config = ProfileConfig.model_validate(profile)
    return config.model_dump() if isinstance(config, BaseModel) else None


if __name__ == "__main__":
    config = load_config()
    print(config)
