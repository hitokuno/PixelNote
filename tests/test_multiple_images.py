def test_multiple_images_and_versions(client):
    img1 = {"image_name": "Image 1", "pixels": [[0, 0, "#111111"]]}
    img2 = {"image_name": "Image 2", "pixels": [[1, 1, "#222222"]]}

    # Create two images
    res1 = client.post("/api/create", json=img1)
    res2 = client.post("/api/create", json=img2)
    assert res1.status_code == 200 and res2.status_code == 200
    id1 = res1.json()["image_id"]
    id2 = res2.json()["image_id"]

    # Update image 1 (to create version 2)
    res = client.post("/api/update", json={"image_id": id1, "pixels": [[2, 2, "#333333"]]})
    assert res.status_code == 200

    # Check version list
    v1 = client.get(f"/api/images/{id1}/versions").json()["versions"]
    v2 = client.get(f"/api/images/{id2}/versions").json()["versions"]
    assert v1 == ["2", "1"]
    assert v2 == ["1"]

    # Check list returns both images
    res = client.get("/api/list")
    images = res.json()["images"]
    ids = [img["image_id"] for img in images]
    assert id1 in ids and id2 in ids