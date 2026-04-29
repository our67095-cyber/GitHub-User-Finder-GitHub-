import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
import threading

FAV_FILE = "favorites.json"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("550x450")
        self.root.resizable(False, False)

        self.favorites = self._load_favorites()
        self._build_ui()

    def _build_ui(self):
        # Поле поиска
        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.pack(fill=tk.X)

        self.search_var = tk.StringVar()
        self.entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry.bind("<Return>", lambda _: self.search_users())

        self.search_btn = ttk.Button(search_frame, text="🔍 Поиск", command=self.search_users)
        self.search_btn.pack(side=tk.RIGHT)

        # Список результатов
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.listbox = tk.Listbox(results_frame, font=("Consolas", 10), selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.listbox, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки избранного
        fav_frame = ttk.Frame(self.root, padding=10)
        fav_frame.pack(fill=tk.X)

        ttk.Button(fav_frame, text="⭐ В избранное", command=self.add_to_favorites).pack(side=tk.LEFT)
        ttk.Button(fav_frame, text="📂 Смотреть избранное", command=self.show_favorites).pack(side=tk.LEFT, padx=10)

    def search_users(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Ошибка ввода", "Поле поиска не должно быть пустым.")
            return

        self.listbox.delete(0, tk.END)
        self.search_btn.config(state="disabled", text="⏳ Загрузка...")
        # Запускаем запрос в фоне, чтобы не блокировать интерфейс
        threading.Thread(target=self._fetch_api, args=(query,), daemon=True).start()

    def _fetch_api(self, query):
        try:
            url = f"https://api.github.com/search/users?q={requests.utils.quote(query)}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            users = data.get("items", [])
            # Безопасное обновление GUI из основного потока
            self.root.after(0, self._update_listbox, users)
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка сети/API", str(e)))
        finally:
            self.root.after(0, lambda: self.search_btn.config(state="normal", text="🔍 Поиск"))

    def _update_listbox(self, users):
        self.listbox.delete(0, tk.END)
        if not users:
            self.listbox.insert(tk.END, "Пользователи не найдены.")
            return
        for user in users:
            self.listbox.insert
