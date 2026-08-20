"""TODO 管理アプリの画面（デザイン）を担当するモジュール。"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from todo_logic import Todo, TodoManager


BG = "#f4f1ea"
PANEL = "#fffdf8"
ACCENT = "#2f6f4e"
ACCENT_HOVER = "#255a3e"
DANGER = "#c45c4a"
DANGER_HOVER = "#a84b3c"
TEXT = "#2b2b2b"
MUTED = "#6b6b6b"
BORDER = "#e2dcd0"
DONE = "#8a8a8a"


class TodoApp:
    def __init__(self, root: tk.Tk, manager: TodoManager | None = None) -> None:
        self.root = root
        self.manager = manager or TodoManager()

        self.root.title("TODO 管理")
        self.root.geometry("480x620")
        self.root.minsize(420, 520)
        self.root.configure(bg=BG)

        self._build_layout()
        self.refresh()

    def _build_layout(self) -> None:
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(24, 8))

        tk.Label(
            header,
            text="TODO 管理",
            font=("Yu Gothic UI", 22, "bold"),
            fg=TEXT,
            bg=BG,
        ).pack(anchor="w")

        tk.Label(
            header,
            text="todoを追加して、終わったら削除できます。",
            font=("Yu Gothic UI", 10),
            fg=MUTED,
            bg=BG,
        ).pack(anchor="w", pady=(4, 0))

        input_card = tk.Frame(self.root, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        input_card.pack(fill="x", padx=28, pady=(16, 8))

        inner = tk.Frame(input_card, bg=PANEL)
        inner.pack(fill="x", padx=14, pady=14)

        self.entry = tk.Entry(
            inner,
            font=("Yu Gothic UI", 12),
            relief="flat",
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.entry.bind("<Return>", lambda _event: self.add_todo())
        self.entry.focus_set()

        self.add_button = tk.Button(
            inner,
            text="追加",
            font=("Yu Gothic UI", 11, "bold"),
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=16,
            command=self.add_todo,
        )
        self.add_button.pack(side="right")

        list_wrap = tk.Frame(self.root, bg=BG)
        list_wrap.pack(fill="both", expand=True, padx=28, pady=(8, 24))

        self.canvas = tk.Canvas(list_wrap, bg=BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(list_wrap, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg=BG)

        self.list_frame.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(self.canvas_window, width=event.width),
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event: tk.Event) -> None:
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def add_todo(self) -> None:
        title = self.entry.get()
        added = self.manager.add(title)
        if added is None:
            messagebox.showinfo("入力エラー", "タスクの内容を入力してください。")
            return
        self.entry.delete(0, tk.END)
        self.refresh()

    def delete_todo(self, todo_id: str) -> None:
        if not messagebox.askyesno("削除の確認", "このタスクを削除しますか？"):
            return
        self.manager.delete(todo_id)
        self.refresh()

    def toggle_todo(self, todo_id: str) -> None:
        self.manager.toggle_done(todo_id)
        self.refresh()

    def refresh(self) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()

        todos = self.manager.list_all()
        if not todos:
            empty = tk.Frame(self.list_frame, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
            empty.pack(fill="x", pady=4)
            tk.Label(
                empty,
                text="まだタスクはありません。上から追加してみましょう。",
                font=("Yu Gothic UI", 10),
                fg=MUTED,
                bg=PANEL,
                pady=28,
            ).pack()
            return

        for todo in todos:
            self._render_item(todo)

    def _render_item(self, todo: Todo) -> None:
        card = tk.Frame(self.list_frame, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=5)

        row = tk.Frame(card, bg=PANEL)
        row.pack(fill="x", padx=12, pady=10)

        check_text = "☑" if todo.done else "☐"
        check_btn = tk.Button(
            row,
            text=check_text,
            font=("Yu Gothic UI", 13),
            bg=PANEL,
            fg=ACCENT if todo.done else MUTED,
            relief="flat",
            cursor="hand2",
            command=lambda todo_id=todo.id: self.toggle_todo(todo_id),
        )
        check_btn.pack(side="left")

        title_color = DONE if todo.done else TEXT
        title_font = ("Yu Gothic UI", 11, "overstrike") if todo.done else ("Yu Gothic UI", 11)
        tk.Label(
            row,
            text=todo.title,
            font=title_font,
            fg=title_color,
            bg=PANEL,
            anchor="w",
            justify="left",
            wraplength=280,
        ).pack(side="left", fill="x", expand=True, padx=8)

        delete_btn = tk.Button(
            row,
            text="削除",
            font=("Yu Gothic UI", 10, "bold"),
            bg=DANGER,
            fg="white",
            activebackground=DANGER_HOVER,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=10,
            command=lambda todo_id=todo.id: self.delete_todo(todo_id),
        )
        delete_btn.pack(side="right")


def main() -> None:
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
