import abc


class StorageBackend(abc.ABC):
    @abc.abstractmethod
    async def upload(
        self, key: str, data: bytes, content_type: str = "application/octet-stream"
    ) -> str:
        ...

    @abc.abstractmethod
    async def download(self, key: str) -> bytes:
        ...

    @abc.abstractmethod
    async def delete(self, key: str) -> bool:
        ...

    @abc.abstractmethod
    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        ...
