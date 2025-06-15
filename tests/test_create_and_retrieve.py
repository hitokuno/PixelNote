import pytest

def test_create_and_retrieve(client):
    image_name = "テスト画像"
    pixels = [[10, 20, "#ff0000"], [30, 40, "#00ff00"]]
    payload = {
        "image_name": image_name,
        "pixels": pixels
    }

    # 画像作成
    res = client.post("/api/create", json=payload)
    assert res.status_code == 200
    image_id = res.json()["image_id"]
    assert image_id

    # 一覧取得
    res = client.get("/api/list")
    assert res.status_code == 200
    images = res.json()["images"]
    assert any(img["image_id"] == image_id for img in images)

    # バージョン一覧取得
    res = client.get(f"/api/images/{image_id}/versions")
    assert res.status_code == 200
    versions = res.json()["versions"]
    assert "1" in versions

    # 描画データ取得
    res = client.get(f"/api/images/{image_id}/1")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data["pixels"], list)
    assert any(p == [10, 20, "#ff0000"] for p in data["pixels"])
    assert any(p == [30, 40, "#00ff00"] for p in data["pixels"])