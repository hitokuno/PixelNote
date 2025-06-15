from typing import List, Tuple, Optional
from abc import ABC, abstractmethod

class DBInterface(ABC):
    @abstractmethod
    async def create_image(self, image_name: str, pixels: List[Tuple[int, int, str]], user_id: str) -> str:
        pass

    @abstractmethod
    async def save_drawing(self, image_id: str, pixels: List[Tuple[int, int, str]], user_id: str) -> str:
        pass

    @abstractmethod
    async def rename_image(self, image_id: str, new_name: str, user_id: str) -> None:
        pass

    @abstractmethod
    async def get_image_list(self) -> List[dict]:
        pass

    @abstractmethod
    async def get_image_versions(self, image_id: str) -> List[str]:
        pass

    @abstractmethod
    async def get_drawing_data(self, image_id: str, version: int) -> Optional[List[Tuple[int, int, str]]]:
        pass