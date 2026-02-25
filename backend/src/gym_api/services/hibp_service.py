import hashlib
import logging

import httpx

logger = logging.getLogger(__name__)
HIBP_API = "https://api.pwnedpasswords.com/range/"


async def check_password_breach(password: str) -> bool:
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{HIBP_API}{prefix}")
            response.raise_for_status()
    except Exception:
        logger.warning("HIBP API unavailable, failing open")
        return False

    for line in response.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix.strip() == suffix:
            return True
    return False
