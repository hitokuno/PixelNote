def test_update_and_rename(client):
    image_name = "アップデート前"
    pixels_v1 = [[1, 1, "#123456"]]
    pixels_v2 = [[2, 2, "#654321"]]

    res = client.post("/api/create", json={"image_name": image_name, "pixels": pixels_v1})
    assert res.status_code == 200
    image_id = res.json()["image_id"]

    res = client.post(f"/api/save/{image_id}", json={"pixels": pixels_v2})
    assert res.status_code == 200
    assert res.json()["version"] == "2"

    res = client.put(f"/api/rename/{image_id}", json={"image_name": "アップデート後"})
    assert res.status_code == 200
