import logging

from gym_api.storage.storage_service import StorageBackend

logger = logging.getLogger(__name__)


class S3Storage(StorageBackend):
    """S3-compatible storage backend.

    Requires boto3 to be installed. For MVP, use LocalStorage instead.
    This provides the interface for production deployment.
    """

    def __init__(self, bucket: str, region: str = "us-east-1", endpoint_url: str | None = None):
        self.bucket = bucket
        self.region = region
        self.endpoint_url = endpoint_url

    def _get_client(self):
        try:
            import boto3
        except ImportError:
            raise RuntimeError("boto3 is required for S3Storage. Install with: pip install boto3")
        kwargs = {"region_name": self.region}
        if self.endpoint_url:
            kwargs["endpoint_url"] = self.endpoint_url
        return boto3.client("s3", **kwargs)

    async def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        client = self._get_client()
        client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        logger.info("S3Storage: uploaded %s to %s", key, self.bucket)
        return f"s3://{self.bucket}/{key}"

    async def download(self, key: str) -> bytes:
        client = self._get_client()
        response = client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    async def delete(self, key: str) -> bool:
        client = self._get_client()
        client.delete_object(Bucket=self.bucket, Key=key)
        return True

    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        client = self._get_client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
