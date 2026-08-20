"""画面操作（追加・削除・空入力）のテスト。"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from todo_logic import TodoManager
from todo_ui import TodoApp


tkinter = pytest.importorskip("tkinter")


@pytest.fixture(scope="module")
def tk_root():
    try:
        root = tkinter.Tk()
    except tkinter.TclError:
        pytest.skip("GUI を表示できない環境です")
    root.withdraw()
    yield root
    try:
        root.destroy()
    except tkinter.TclError:
        pass


@pytest.fixture
def app(tmp_path: Path, tk_root):
    for child in tk_root.winfo_children():
        child.destroy()
    manager = TodoManager(data_file=tmp_path / "todos.json")
    window = TodoApp(tk_root, manager=manager)
    yield window
    tk_root.unbind_all("<MouseWheel>")


def test_add_todo_from_entry(app: TodoApp) -> None:
    app.entry.insert(0, "テストタスク")
    app.add_todo()

    todos = app.manager.list_all()
    assert len(todos) == 1
    assert todos[0].title == "テストタスク"
    assert app.entry.get() == ""


def test_add_todo_rejects_blank_input(app: TodoApp) -> None:
    with patch("todo_ui.messagebox.showinfo") as showinfo:
        app.add_todo()

    showinfo.assert_called_once()
    assert app.manager.list_all() == []


def test_delete_todo_when_confirmed(app: TodoApp) -> None:
    todo = app.manager.add("消す")
    assert todo is not None
    app.refresh()

    with patch("todo_ui.messagebox.askyesno", return_value=True):
        app.delete_todo(todo.id)

    assert app.manager.list_all() == []


def test_delete_todo_when_cancelled(app: TodoApp) -> None:
    todo = app.manager.add("残す")
    assert todo is not None
    app.refresh()

    with patch("todo_ui.messagebox.askyesno", return_value=False):
        app.delete_todo(todo.id)

    assert len(app.manager.list_all()) == 1


def test_subtitle_uses_todo_wording(app: TodoApp) -> None:
    labels = [
        child.cget("text")
        for child in app.root.winfo_children()[0].winfo_children()
        if child.winfo_class() == "Label"
    ]
    assert any("todoを追加して" in text for text in labels)
