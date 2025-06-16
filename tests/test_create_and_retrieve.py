def test_create_and_retrieve(client):
    image_name = "テスト画像"
    pixels = [[10, 20, "#ff0000"], [30, 40, "#00ff00"]]
    payload = {
        "image_name": image_name,
        "pixels": pixels
    }

    res = client.post("/api/create", json=payload)
    assert res.status_code == 200
    image_id = res.json()["image_id"]

    res_list = client.get("/api/list")
    assert res_list.status_code == 200
    assert any(img["image_id"] == image_id for img in res_list.json())

    res_versions = client.get(f"/api/images/{image_id}/versions")
    assert res_versions.status_code == 200
    assert res_versions.json() == ["1"]

    res_data = client.get(f"/api/images/{image_id}/1")
    assert res_data.status_code == 200
    assert res_data.json()["pixels"] == pixels
