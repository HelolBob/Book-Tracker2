import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер прочитанных книг")
        self.root.geometry("950x650")

        self.books = []
        self.load_data()

        # Рамка для добавления книги
        input_frame = tk.LabelFrame(root, text="Добавить книгу", padx=10, pady=10, font=("Arial", 10, "bold"))
        input_frame.pack(fill="x", padx=10, pady=5)

        # Название книги
        tk.Label(input_frame, text="Название книги:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = tk.Entry(input_frame, width=25)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Автор
        tk.Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.author_entry = tk.Entry(input_frame, width=20)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)

        # Жанр
        tk.Label(input_frame, text="Жанр:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.genre_var = tk.StringVar()
        genres = ["Художественная литература", "Детектив", "Фантастика", "Научная",
                  "Биография", "Поэзия", "Драма", "Комедия", "Приключения", "Роман", "Другое"]
        self.genre_combo = ttk.Combobox(input_frame, textvariable=self.genre_var, values=genres, width=18)
        self.genre_combo.grid(row=0, column=5, padx=5, pady=5)
        self.genre_combo.current(0)

        # Количество страниц
        tk.Label(input_frame, text="Страниц:").grid(row=0, column=6, sticky="w", padx=5, pady=5)
        self.pages_entry = tk.Entry(input_frame, width=8)
        self.pages_entry.grid(row=0, column=7, padx=5, pady=5)

        # Кнопка добавления
        self.add_btn = tk.Button(input_frame, text="Добавить книгу", command=self.add_book, bg="green", fg="white", font=("Arial", 9, "bold"))
        self.add_btn.grid(row=0, column=8, padx=10, pady=5)

        # Рамка фильтрации
        filter_frame = tk.LabelFrame(root, text="Фильтрация книг", padx=10, pady=10, font=("Arial", 10, "bold"))
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        tk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filter_genre_var = tk.StringVar()
        self.filter_genre_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var, values=["Все"] + genres, width=18)
        self.filter_genre_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_genre_combo.current(0)

        # Фильтр по количеству страниц
        tk.Label(filter_frame, text="Страниц больше:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.filter_pages_entry = tk.Entry(filter_frame, width=8)
        self.filter_pages_entry.grid(row=0, column=3, padx=5, pady=5)
        self.filter_pages_entry.insert(0, "0")

        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter, bg="blue", fg="white")
        self.filter_btn.grid(row=0, column=4, padx=10, pady=5)

        self.reset_filter_btn = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_btn.grid(row=0, column=5, padx=5, pady=5)

        # Рамка статистики
        stats_frame = tk.Frame(root)
        stats_frame.pack(fill="x", padx=10, pady=5)
        self.stats_label = tk.Label(stats_frame, text="Всего книг: 0 | Всего страниц: 0", font=("Arial", 11, "bold"))
        self.stats_label.pack(side="left")

        # Таблица с книгами
        columns = ("ID", "Title", "Author", "Genre", "Pages")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Название книги")
        self.tree.heading("Author", text="Автор")
        self.tree.heading("Genre", text="Жанр")
        self.tree.heading("Pages", text="Страниц")

        self.tree.column("ID", width=50)
        self.tree.column("Title", width=250)
        self.tree.column("Author", width=180)
        self.tree.column("Genre", width=180)
        self.tree.column("Pages", width=80)

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Кнопка удаления
        delete_frame = tk.Frame(root)
        delete_frame.pack(fill="x", padx=10, pady=5)
        self.delete_btn = tk.Button(delete_frame, text="Удалить выбранную книгу", command=self.delete_book, bg="red", fg="white", font=("Arial", 9, "bold"))
        self.delete_btn.pack(side="left", padx=5)

        self.refresh_table()

    def add_book(self):
        # Проверка названия
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Ошибка ввода", "Название книги не может быть пустым.")
            return

        # Проверка автора
        author = self.author_entry.get().strip()
        if not author:
            messagebox.showerror("Ошибка ввода", "Автор не может быть пустым.")
            return

        # Проверка жанра
        genre = self.genre_var.get().strip()
        if not genre:
            messagebox.showerror("Ошибка ввода", "Выберите жанр.")
            return

        # Проверка количества страниц
        try:
            pages = int(self.pages_entry.get().strip())
            if pages <= 0:
                raise ValueError("Количество страниц должно быть положительным")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Количество страниц должно быть целым положительным числом.")
            return

        # Добавление книги
        new_id = max([b["id"] for b in self.books], default=0) + 1
        self.books.append({
            "id": new_id,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        })
        self.save_data()
        self.refresh_table()

        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)
        self.pages_entry.insert(0, "0")

        messagebox.showinfo("Успех", f"Книга «{title}» успешно добавлена!")

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ничего не выбрано", "Выберите книгу для удаления.")
            return
        item = self.tree.item(selected[0])
        book_id = item["values"][0]

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту книгу?"):
            self.books = [b for b in self.books if b["id"] != book_id]
            self.save_data()
            self.refresh_table()
            self.apply_filter()
            messagebox.showinfo("Успех", "Книга удалена.")

    def apply_filter(self):
        genre_filter = self.filter_genre_var.get()
        pages_filter_str = self.filter_pages_entry.get().strip()

        filtered = self.books[:]

        # Фильтр по жанру
        if genre_filter != "Все":
            filtered = [b for b in filtered if b["genre"] == genre_filter]

        # Фильтр по страницам
        try:
            pages_filter = int(pages_filter_str) if pages_filter_str else 0
            filtered = [b for b in filtered if b["pages"] > pages_filter]
        except ValueError:
            if pages_filter_str:
                messagebox.showwarning("Ошибка формата", "Количество страниц должно быть числом.")

        # Обновление статистики
        total_books = len(filtered)
        total_pages = sum(b["pages"] for b in filtered)
        self.stats_label.config(text=f"Всего книг: {total_books} | Всего страниц: {total_pages}")

        # Обновление таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        for book in filtered:
            self.tree.insert("", tk.END, values=(book["id"], book["title"], book["author"], book["genre"], book["pages"]))

    def reset_filter(self):
        self.filter_genre_var.set("Все")
        self.filter_pages_entry.delete(0, tk.END)
        self.filter_pages_entry.insert(0, "0")
        self.refresh_table()

    def refresh_table(self):
        # Сброс фильтров
        self.filter_genre_var.set("Все")
        self.filter_pages_entry.delete(0, tk.END)
        self.filter_pages_entry.insert(0, "0")

        # Обновление статистики
        total_books = len(self.books)
        total_pages = sum(b["pages"] for b in self.books)
        self.stats_label.config(text=f"Всего книг: {total_books} | Всего страниц: {total_pages}")

        # Обновление таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        for book in self.books:
            self.tree.insert("", tk.END, values=(book["id"], book["title"], book["author"], book["genre"], book["pages"]))

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.books, f, indent=4, ensure_ascii=False)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.books = []

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()
