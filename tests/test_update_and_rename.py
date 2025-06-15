import pytest

def test_update_and_rename(client):
    image_name = "アップデート前"
    pixels_v1 = [[1, 1, "#123456"]]
    pixels_v2 = [[2, 2, "#654321"]]

    # 初回保存
    res = client.post("/api/create", json={"image_name": image_name, "pixels": pixels_v1})
    assert res.status_code == 200
    image_id = res.json()["image_id"]

    # 更新（バージョン2保存）
    res = client.post("/api/update", json={"image_id": image_id, "pixels": pixels_v2})
    assert res.status_code == 200
    version2 = res.json()["version"]
    assert version2 == "2"

    # バージョン2の描画データ取得
    res = client.get(f"/api/images/{image_id}/2")
    assert res.status_code == 200
    pixels = res.json()["pixels"]
    assert any(p == [2, 2, "#654321"] for p in pixels)

    # 名前変更
    new_name = "リネーム後"
    res = client.post("/api/rename", json={"image_id": image_id, "image_name": new_name})
    assert res.status_code == 200

    # 一覧で名前が変わっていることを確認
    res = client.get("/api/list")
    images = res.json()["images"]
    match = next((img for img in images if img["image_id"] == image_id), None)
    assert match is not None
    assert match["image_name"] == new_name