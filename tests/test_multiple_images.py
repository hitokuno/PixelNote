from tests.utils import assert_with_debug

def test_multiple_images_and_versions(client):
    img1 = {"image_name": "Image 1", "pixels": [{"x":0, "y":0, "rgb":"#111111"}]}
    img2 = {"image_name": "Image 2", "pixels": [{"x":1, "y":1, "rgb": "#222222"}]}

    res1 = client.post("/api/create", json=img1)
    res2 = client.post("/api/create", json=img2)
    assert_with_debug(res1.status_code == 200, res1)
    assert_with_debug(res2.status_code == 200, res2)

    id1 = res1.json()["image_id"]
    id2 = res2.json()["image_id"]

    client.post("/api/save", json={"image_id": id1, "pixels": [{"x":2, "y":2, "rgb":"#333333"}]})
    client.post("/api/save", json={"image_id": id2, "pixels": [{"x":3, "y":3, "rgb":"#444444"}]})

    versions1 = client.get(f"/api/images/{id1}/versions")
    versions2 = client.get(f"/api/images/{id2}/versions")
    assert_with_debug(versions1.status_code == 200, versions1)
    assert_with_debug(versions2.status_code == 200, versions2)
    assert_with_debug(versions1.json() == ["1", "2"], versions1)
    assert_with_debug(versions2.json() == ["1", "2"], versions2)

def test_list_and_versions_are_desc_order(client):
    # 複数画像作成
    image_ids = []
    for i in range(3):
        res = client.post("/api/create", json={
            "image_name": f"テスト{i}",
            "pixels": [{"x":i, "y":i, "rgb":"#123456"}]
        })
        image_ids.append(res.json()["image_id"])

    # 一覧のlast_modified_at降順チェック
    res = client.get("/api/list")
    last_modified_list = [img["last_modified_at"] for img in res.json()]
    assert_with_debug(last_modified_list == sorted(last_modified_list, reverse=True) == ["2", "1"], res)

    # バージョンのcreated_at降順チェック
    for image_id in image_ids:
        client.post("/api/save", json={"image_id": image_id, "pixels": [{"x":9, "y":9, "rgb":"#ff0000"}]})
        versions = client.get(f"/api/images/{image_id}/versions").json()
        # バージョン番号の降順（"2", "1"...）であること
        assert_with_debug(versions == sorted(versions, reverse=True), versions)
