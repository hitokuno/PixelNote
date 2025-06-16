def test_create_image_with_long_name(client):
    image_name = "A" * 300  # 長すぎてエラーになる場合あり
    pixels = [[1, 1, "#000000"]]
    payload = {"image_name": image_name, "pixels": pixels}
    res = client.post("/api/create", json=payload)
    assert res.status_code != 200

def test_rename_image_not_exist(client):
    res = client.post("/api/rename", json={"image_id": "not_exist", "new_name": "fail"})
    assert res.status_code != 200 or res.json().get("status") != "ok"