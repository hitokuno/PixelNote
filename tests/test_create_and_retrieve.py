from tests.utils import assert_with_debug

def test_create_and_retrieve(client):
    payload = {
        "image_name": "テスト画像",
        "pixels": [
            {"x": 10, "y": 20, "rgb": "#ff0000"},
            {"x": 30, "y": 40, "rgb": "#00ff00"}
        ]
    }
    res = client.post("/api/create", json=payload)
    assert_with_debug(res.status_code == 200, res)
    image_id = res.json()["image_id"]

    res_list = client.get("/api/list")
    assert_with_debug(res_list.status_code == 200, res_list)
    
    images = res_list.json()["images"]
    found = [img for img in images if img["image_id"] == image_id]
    assert_with_debug(found, res_list, msg=f"images: {images}")
    img = found[0]
    for k in ["image_id", "image_name", "last_modified_by", "last_modified_at"]:
        assert_with_debug(k in img, res_list, msg=f"key {k} missing in {img}")


    res_versions = client.get(f"/api/images/{image_id}/versions")
    assert_with_debug(res.status_code == 200, res)
    assert_with_debug(res_versions.json() == ["1"], res_versions)

    res_data = client.get(f"/api/images/{image_id}/1")
    assert_with_debug(res.status_code == 200, res)
    assert_with_debug(res_data.json()["pixels"] == pixels, res_data)
