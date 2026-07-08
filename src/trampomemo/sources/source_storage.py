from pathlib import Path
from typing import Protocol
from uuid import uuid4


class SourceStorage(Protocol):
    def save_bytes(self, *, original_filename: str, content: bytes) -> str:
        raise NotImplementedError

    def save_text(self, *, content: str) -> str:
        raise NotImplementedError

    def read_bytes(self, *, storage_uri: str) -> bytes:
        raise NotImplementedError

    def read_text(self, *, storage_uri: str) -> str:
        raise NotImplementedError


class LocalSourceStorage:
    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path

    def save_bytes(self, *, original_filename: str, content: bytes) -> str:
        self.root_path.mkdir(parents=True, exist_ok=True)
        suffix = Path(original_filename).suffix.lower()
        key = f"{uuid4()}{suffix}"
        path = self.root_path / key
        path.write_bytes(content)
        return f"local://sources/{key}"

    def save_text(self, *, content: str) -> str:
        self.root_path.mkdir(parents=True, exist_ok=True)
        key = f"{uuid4()}.txt"
        path = self.root_path / key
        path.write_text(content, encoding="utf-8")
        return f"local://sources/{key}"

    def read_bytes(self, *, storage_uri: str) -> bytes:
        return self._path_for(storage_uri).read_bytes()

    def read_text(self, *, storage_uri: str) -> str:
        return self._path_for(storage_uri).read_text(encoding="utf-8")

    def _path_for(self, storage_uri: str) -> Path:
        prefix = "local://sources/"
        if not storage_uri.startswith(prefix):
            raise ValueError("Unsupported Source storage URI.")

        key = storage_uri.removeprefix(prefix)
        path = self.root_path / key
        if path.parent != self.root_path:
            raise ValueError("Invalid Source storage URI.")

        return path
