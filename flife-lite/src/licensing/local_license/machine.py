from __future__ import annotations

import hashlib
import platform
import uuid


def machine_hash() -> str:
    raw = "|".join(
        [
            platform.node(),
            platform.machine(),
            platform.processor(),
            str(uuid.getnode()),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
