def test_not_found_errors(client):
    fake_image_id = "00000000-0000-0000-0000-000000000000"

    # 存在しない image_id でバージョン取得
    res = client.get(f"/api/images/{fake_image_id}/versions")
    assert res.status_code == 404 or res.status_code == 400

    # 存在しない image_id + version で描画データ取得
    res = client.get(f"/api/images/{fake_image_id}/999")
    assert res.status_code == 404 or res.status_code == 400

    # 不正な image_id で rename 実行
    res = client.post("/api/rename", json={"image_id": fake_image_id, "image_name": "test"})
    assert res.status_code in [400, 404]

    # 不正な image_id で update 実行
    res = client.post("/api/update", json={"image_id": fake_image_id, "pixels": [[0, 0, "#000000"]]})
    assert res.status_code in [400, 404]