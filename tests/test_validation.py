from tests.utils import assert_with_debug

def test_image_name_length(client):
    long_name = "あ" * 256
    pixels = [{"x":0, "y":0, "rgb":"#123456"}]
    res = client.post("/api/create", json={"image_name": long_name, "pixels": pixels})
    print(f"status:{res.status_code}, body:{res.text}, json:{res.json()}")
    assert_with_debug(res.status_code == 400, res)
    errors = res.json()["errors"]
    assert any("image_name" in err["field"] and "255文字以内" in err["message"] for err in errors)

def test_rgb_length(client):
    bad_rgb = "#1234567"
    pixels = [{"x":0, "y":0, "rgb":bad_rgb}]
    res = client.post("/api/create", json={"image_name": "ok", "pixels": pixels})
    assert_with_debug(res.status_code == 400, res)
    errors = res.json()["errors"]
    assert any("rgb" in err["field"] and "7文字以内" in err["message"] for err in errors)

def test_image_id_length(client):
    too_long = "x" * 37
    res = client.post("/api/rename", json={"image_id": too_long, "new_name": "abc"})
    assert_with_debug(res.status_code == 400, res)
    errors = res.json()["errors"]
    assert any("image_id" in err["field"] and "36文字以内" in err["message"] for err in errors)

def test_new_name_length(client):
    too_long = "a" * 256
    # image_idには正しい長さの値を入れること
    res = client.post("/api/rename", json={"image_id": "abc123", "new_name": too_long})
    assert_with_debug(res.status_code == 400, res)
    errors = res.json()["errors"]
    assert any("new_name" in err["field"] and "255文字以内" in err["message"] for err in errors)
