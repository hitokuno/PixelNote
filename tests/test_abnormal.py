from tests.utils import assert_with_debug

def test_create_image_with_long_name(client):
    image_name = "A" * 300  # 長すぎてエラーになる場合あり
    pixels = [{"x":1, "y":1, "rgb":"#000000"}]
    payload = {"image_name": image_name, "pixels": pixels}
    res = client.post("/api/create", json=payload)
    assert_with_debug(res.status_code == 400, res)
    js = res.json()
    assert any(e["field"] == "image_id" and "255文字以内で指定してください" in e["message"] for e in js["errors"])

def test_rename_image_not_exist(client):
    res = client.post("/api/rename", json={"image_id": "not_exist", "new_name": "fail"})
    assert_with_debug(res.status_code == 400, res)
    js = res.json()
    assert any(e["field"] == "image_id" and "指定したimage_idが存在しません" in e["message"] for e in js["errors"])