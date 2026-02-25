import logging
from pathlib import Path

from gym_api.storage.storage_service import StorageBackend

logger = logging.getLogger(__name__)

DEFAULT_STORAGE_DIR = Path("storage_data")


class LocalStorage(StorageBackend):
    def __init__(self, base_dir: Path | str = DEFAULT_STORAGE_DIR):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe_key = key.replace("..", "").lstrip("/")
        return self.base_dir / safe_key

    async def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        logger.info("LocalStorage: uploaded %s (%d bytes)", key, len(data))
        return str(path)

    async def download(self, key: str) -> bytes:
        path = self._path(key)
        if not path.exists():
            raise FileNotFoundError(f"Object not found: {key}")
        return path.read_bytes()

    async def delete(self, key: str) -> bool:
        path = self._path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        return f"/files/{key}"
