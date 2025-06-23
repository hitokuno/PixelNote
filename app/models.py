# app/models.py

class ImageName:
    def __init__(self, image_id: str, image_name: str, last_modified_by: str, last_modified_at):
        self.image_id = image_id
        self.image_name = image_name
        self.last_modified_by = last_modified_by
        self.last_modified_at = last_modified_at

    def to_dict(self):
        return {
            "image_id": self.image_id,
            "image_name": self.image_name,
            "last_modified_by": self.last_modified_by,
            "last_modified_at": self.last_modified_at
        }

class Drawing:
    def __init__(self, drawing_id: int, image_id: str, version: int, created_at, created_by: str):
        self.drawing_id = drawing_id
        self.image_id = image_id
        self.version = version
        self.created_at = created_at
        self.created_by = created_by

    def to_dict(self):
        return {
            "drawing_id": self.drawing_id,
            "image_id": self.image_id,
            "version": self.version,
            "created_at": self.created_at,
            "created_by": self.created_by
        }

class Pixel:
    def __init__(self, drawing_id: int, x: int, y: int, rgb: str):
        self.drawing_id = drawing_id
        self.x = x
        self.y = y
        self.rgb = rgb

    def to_dict(self):
        return {
            "drawing_id": self.drawing_id,
            "x": self.x,
            "y": self.y,
            "rgb": self.rgb
        }
