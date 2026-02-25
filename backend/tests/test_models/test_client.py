import uuid

from gym_api.models.client import Client, ClientStatus, Gender


def test_client_instantiation():
    client = Client(
        gym_id=uuid.uuid4(),
        first_name="Jane",
        last_name="Doe",
        status=ClientStatus.active,
    )
    assert client.first_name == "Jane"
    assert client.status == ClientStatus.active
    assert client.email is None
    assert client.gender is None


def test_client_status_enum():
    assert ClientStatus.active.value == "active"
    assert ClientStatus.inactive.value == "inactive"
    assert ClientStatus.suspended.value == "suspended"


def test_gender_enum():
    assert Gender.male.value == "male"
    assert Gender.prefer_not_to_say.value == "prefer_not_to_say"
