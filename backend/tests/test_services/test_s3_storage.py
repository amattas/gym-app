
from gym_api.storage.s3_storage import S3Storage


def test_s3_storage_requires_boto3():
    storage = S3Storage(bucket="test-bucket")
    # _get_client should raise if boto3 is not installed
    # (or succeed if it is — both are valid for this test)
    try:
        client = storage._get_client()
        # boto3 is installed — that's fine
        assert client is not None
    except RuntimeError as e:
        assert "boto3" in str(e)


def test_s3_storage_init():
    storage = S3Storage(bucket="my-bucket", region="eu-west-1")
    assert storage.bucket == "my-bucket"
    assert storage.region == "eu-west-1"


def test_s3_storage_custom_endpoint():
    storage = S3Storage(
        bucket="my-bucket",
        endpoint_url="http://localhost:9000",
    )
    assert storage.endpoint_url == "http://localhost:9000"
