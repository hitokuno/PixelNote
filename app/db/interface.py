from typing import List, Tuple, Optional

class DBInterface:
    async def create_image(self, image_name: str, pixels: List[Tuple[int, int, str]], user_id: str) -> str:
        ...

    async def save_drawing(self, image_id: str, pixels: List[Tuple[int, int, str]], user_id: str) -> str:
        ...

    async def rename_image(self, image_id: str, new_name: str, user_id: str) -> None:
        ...

    async def get_image_list(self) -> List[dict]:
        ...

    async def get_image_versions(self, image_id: str) -> List[str]:
        ...

    async def get_drawing_data(self, image_id: str, version: int) -> Optional[List[Tuple[int, int, str]]]:
        ...
