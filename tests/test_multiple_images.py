def test_multiple_images_and_versions(client):
    img1 = {"image_name": "Image 1", "pixels": [[0, 0, "#111111"]]}
    img2 = {"image_name": "Image 2", "pixels": [[1, 1, "#222222"]]}

    res1 = client.post("/api/create", json=img1)
    res2 = client.post("/api/create", json=img2)
    assert res1.status_code == 200 and res2.status_code == 200

    id1 = res1.json()["image_id"]
    id2 = res2.json()["image_id"]

    client.post(f"/api/save/{id1}", json={"pixels": [[2, 2, "#333333"]]})
    client.post(f"/api/save/{id2}", json={"pixels": [[3, 3, "#444444"]]})

    versions1 = client.get(f"/api/images/{id1}/versions")
    versions2 = client.get(f"/api/images/{id2}/versions")
    assert versions1.status_code == 200
    assert versions2.status_code == 200
    assert versions1.json() == ["2", "1"]
    assert versions2.json() == ["2", "1"]
