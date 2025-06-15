import pytest

@pytest.mark.parametrize("payload", [
    {"image_name": "Invalid RGB", "pixels": [[0, 0, "red"]]},           # invalid RGB
    {"image_name": "Negative Coord", "pixels": [[-1, -1, "#123456"]]},  # negative coordinates
    {"image_name": "Too Long", "pixels": [[0, 0, "#123456"]] * 100000}, # too many pixels
    {"image_name": "Empty", "pixels": []},                              # no pixels
])
def test_invalid_create(client, payload):
    res = client.post("/api/create", json=payload)
    assert res.status_code >= 400