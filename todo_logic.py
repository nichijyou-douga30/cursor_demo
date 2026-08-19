"""TODO の追加・削除など、データの処理を担当するモジュール。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import uuid


DATA_FILE = Path(__file__).with_name("todos.json")


@dataclass
class Todo:
    id: str
    title: str
    done: bool = False


class TodoManager:
    def __init__(self, data_file: Path = DATA_FILE) -> None:
        self.data_file = data_file
        self.todos: list[Todo] = []
        self.load()

    def load(self) -> None:
        if not self.data_file.exists():
            self.todos = []
            return
        try:
            raw = json.loads(self.data_file.read_text(encoding="utf-8"))
            self.todos = [Todo(**item) for item in raw]
        except (json.JSONDecodeError, TypeError, KeyError):
            self.todos = []

    def save(self) -> None:
        payload = [asdict(todo) for todo in self.todos]
        self.data_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, title: str) -> Todo | None:
        cleaned = title.strip()
        if not cleaned:
            return None
        todo = Todo(id=str(uuid.uuid4()), title=cleaned)
        self.todos.append(todo)
        self.save()
        return todo

    def delete(self, todo_id: str) -> bool:
        before = len(self.todos)
        self.todos = [todo for todo in self.todos if todo.id != todo_id]
        if len(self.todos) == before:
            return False
        self.save()
        return True

    def toggle_done(self, todo_id: str) -> bool:
        for todo in self.todos:
            if todo.id == todo_id:
                todo.done = not todo.done
                self.save()
                return True
        return False

    def list_all(self) -> list[Todo]:
        return list(self.todos)
