from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from app.config import settings


def load_seed_data() -> dict[str, Any]:
    with settings.seed_data_path.open("r", encoding="utf-8") as handle:
        return deepcopy(json.load(handle))

