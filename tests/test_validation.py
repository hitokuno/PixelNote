def test_image_name_too_long(client):
    pixels = [{"x":0, "y":0, "rgb":"#123456"}]
    res = client.post("/api/create", json={"image_name": "A"*256, "pixels": pixels})
    assert res.status_code == 400
    js = res.json()
    assert "errors" in js
    assert js["errors"][0]["field"] == "image_name"
    assert "255文字" in js["errors"][0]["message"]

def test_invalid_rgb(client):
    pixels = [{"x":0, "y":0, "rgb":"GGG"}]
    res = client.post("/api/create", json={"image_name": "test", "pixels": pixels})
    assert res.status_code == 400
    js = res.json()
    assert js["errors"][0]["field"] == "pixels.0.rgb"
    assert "hex format" in js["errors"][0]["message"]
