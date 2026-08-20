"""TodoManager の追加・削除・完了切替・保存のテスト。"""

from __future__ import annotations

import json
from pathlib import Path

from todo_logic import TodoManager


def make_manager(tmp_path: Path) -> TodoManager:
    return TodoManager(data_file=tmp_path / "todos.json")


def test_add_saves_task(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)

    todo = manager.add("牛乳を買う")

    assert todo is not None
    assert todo.title == "牛乳を買う"
    assert todo.done is False
    assert len(manager.list_all()) == 1


def test_add_strips_whitespace(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)

    todo = manager.add("  掃除  ")

    assert todo is not None
    assert todo.title == "掃除"


def test_add_rejects_empty_title(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)

    assert manager.add("") is None
    assert manager.add("   ") is None
    assert manager.list_all() == []
    assert not manager.data_file.exists()


def test_delete_removes_task(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    todo = manager.add("捨てるタスク")
    assert todo is not None

    assert manager.delete(todo.id) is True
    assert manager.list_all() == []


def test_delete_unknown_id_returns_false(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    manager.add("残すタスク")

    assert manager.delete("missing-id") is False
    assert len(manager.list_all()) == 1


def test_toggle_done(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    todo = manager.add("完了にする")
    assert todo is not None

    assert manager.toggle_done(todo.id) is True
    assert manager.list_all()[0].done is True

    assert manager.toggle_done(todo.id) is True
    assert manager.list_all()[0].done is False


def test_toggle_unknown_id_returns_false(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)

    assert manager.toggle_done("missing-id") is False


def test_list_all_returns_a_copy(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    manager.add("コピー確認")

    listed = manager.list_all()
    listed.clear()

    assert len(manager.list_all()) == 1


def test_tasks_persist_to_json(tmp_path: Path) -> None:
    data_file = tmp_path / "todos.json"
    first = TodoManager(data_file=data_file)
    added = first.add("再起動後も残る")
    assert added is not None

    second = TodoManager(data_file=data_file)
    todos = second.list_all()

    assert len(todos) == 1
    assert todos[0].title == "再起動後も残る"
    assert todos[0].id == added.id


def test_load_ignores_broken_json(tmp_path: Path) -> None:
    data_file = tmp_path / "todos.json"
    data_file.write_text("{not-json", encoding="utf-8")

    manager = TodoManager(data_file=data_file)

    assert manager.list_all() == []


def test_load_ignores_invalid_shape(tmp_path: Path) -> None:
    data_file = tmp_path / "todos.json"
    data_file.write_text(json.dumps([{"title": "idがない"}]), encoding="utf-8")

    manager = TodoManager(data_file=data_file)

    assert manager.list_all() == []
