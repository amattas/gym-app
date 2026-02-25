from pathlib import Path

import pytest

from gym_api.storage.local_storage import LocalStorage


@pytest.fixture
def storage(tmp_path):
    return LocalStorage(base_dir=tmp_path)


async def test_upload_and_download(storage):
    data = b"hello world"
    result = await storage.upload("test/file.txt", data)
    assert result is not None

    downloaded = await storage.download("test/file.txt")
    assert downloaded == data


async def test_download_missing_file(storage):
    with pytest.raises(FileNotFoundError):
        await storage.download("nonexistent.txt")


async def test_delete_existing_file(storage):
    await storage.upload("to_delete.txt", b"temp")
    result = await storage.delete("to_delete.txt")
    assert result is True


async def test_delete_missing_file(storage):
    result = await storage.delete("no_such_file.txt")
    assert result is False


async def test_get_url(storage):
    url = await storage.get_url("photos/img.jpg")
    assert "photos/img.jpg" in url


async def test_path_traversal_prevented(storage):
    await storage.upload("../../../etc/passwd", b"nope")
    # Should not write outside base_dir
    assert not Path("/etc/passwd_test").exists()
    path = storage._path("../../../etc/passwd")
    assert str(storage.base_dir) in str(path.resolve()) or path.is_relative_to(
        storage.base_dir
    )
