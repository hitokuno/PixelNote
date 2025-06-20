def test_multiple_images_and_versions(client):
    img1 = {"image_name": "Image 1", "pixels": [[0, 0, "#111111"]]}
    img2 = {"image_name": "Image 2", "pixels": [[1, 1, "#222222"]]}

    res1 = client.post("/api/create", json=img1)
    res2 = client.post("/api/create", json=img2)
    assert res1.status_code == 200 and res2.status_code == 200

    id1 = res1.json()["image_id"]
    id2 = res2.json()["image_id"]

    client.post("/api/save", json={"image_id": id1, "pixels": [[2, 2, "#333333"]]})
    client.post("/api/save", json={"image_id": id2, "pixels": [[3, 3, "#444444"]]})

    versions1 = client.get(f"/api/images/{id1}/versions")
    versions2 = client.get(f"/api/images/{id2}/versions")
    assert versions1.status_code == 200
    assert versions2.status_code == 200
    assert versions1.json() == ["2", "1"]
    assert versions2.json() == ["2", "1"]

def test_list_and_versions_are_desc_order(client):
    # 複数画像作成
    image_ids = []
    for i in range(3):
        res = client.post("/api/create", json={
            "image_name": f"テスト{i}",
            "pixels": [[i, i, "#123456"]]
        })
        image_ids.append(res.json()["image_id"])

    # 一覧のlast_modified_at降順チェック
    res = client.get("/api/list")
    last_modified_list = [img["last_modified_at"] for img in res.json()]
    assert last_modified_list == sorted(last_modified_list, reverse=True)

    # バージョンのcreated_at降順チェック
    for image_id in image_ids:
        client.post("/api/save", json={"image_id": image_id, "pixels": [[9,9,"#ff0000"]]})
        versions = client.get(f"/api/images/{image_id}/versions").json()
        # バージョン番号の降順（"2", "1"...）であること
        assert versions == sorted(versions, reverse=True)