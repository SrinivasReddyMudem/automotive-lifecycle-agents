"""
Structured logger for sdk_agents.
Logs raw API responses and parsed output for debugging and audit trail.
"""

import logging
import json
from pathlib import Path

LOGS_DIR = Path(__file__).parents[1] / "logs"


def get_logger(agent_name: str) -> logging.Logger:
    LOGS_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger(f"sdk_agents.{agent_name}")
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG)

    # File handler — full detail for debugging
    fh = logging.FileHandler(LOGS_DIR / f"{agent_name}.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Console handler — errors only
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
