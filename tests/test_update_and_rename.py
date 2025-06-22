from tests.utils import assert_with_debug

def test_update_and_rename(client):
    image_name = "アップデート前"
    pixels_v1 = [{"x":1, "y":1, "rgb": "#123456"}]
    pixels_v2 = [{"x":2, "y":2, "rgb":"#654321"}]

    res = client.post("/api/create", json={"image_name": image_name, "pixels": pixels_v1})
    assert res.status_code == 200
    image_id = res.json()["image_id"]

    res = client.post("/api/save", json={"image_id": image_id, "pixels": pixels_v2})
    assert res.status_code == 200
    assert res.json()["version"] == "2"

    # Rename API を追記する場合はここで検証
