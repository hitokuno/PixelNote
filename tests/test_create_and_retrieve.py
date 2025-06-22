from tests.utils import assert_with_debug

def test_create_and_retrieve(client):
    image_name = "テスト画像"
    pixels = [{"x":10, "y":20, "rgb":"#ff0000"}, {"x":30, "y":40, "rgb":"#00ff00"}]
    payload = {
        "image_name": image_name,
        "pixels": pixels
    }

    res = client.post("/api/create", json=payload)
    assert_with_debug(res.status_code == 200, res)
    image_id = res.json()["image_id"]

    res_list = client.get("/api/list")
    assert_with_debug(res.status_code == 200, res)
    assert any(img["image_id"] == image_id for img in res_list.json())

    res_versions = client.get(f"/api/images/{image_id}/versions")
    assert_with_debug(res.status_code == 200, res)
    assert res_versions.json() == ["1"]

    res_data = client.get(f"/api/images/{image_id}/1")
    assert_with_debug(res.status_code == 200, res)
    assert res_data.json()["pixels"] == pixels
