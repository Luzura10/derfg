import tkinter as tk
from tkinter import ttk, messagebox
import os
import sqlite3
from datetime import datetime

# Импортируем модули приложения
from database import Database
from equipment import EquipmentFrame
from booking import BookingFrame
from ui_styles import configure_styles
from data_generator import show_generator_dialog


class VREquipmentApp(tk.Tk):
    """Основной класс приложения для учета и бронирования VR-оборудования"""

    def __init__(self):
        super().__init__()

        # Инициализация базы данных
        self.db = Database()

        # Настройка основного окна
        self.title("Учет и бронирование VR-оборудования")
        self.geometry("1000x700")
        self.minsize(800, 600)

        # Настройка стилей
        self.style = ttk.Style()
        configure_styles(self.style)

        # Устанавливаем общий фон приложения
        self.configure(background="#f5f5f5")

        # Создаем меню
        self._create_menu()

        # Создаем и размещаем виджеты
        self._create_widgets()

        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_menu(self):
        """Создание главного меню приложения"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="О программе", command=self._show_about)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self._on_close)

        # Меню "Инструменты"
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Генерация тестовых данных", command=self._show_data_generator)

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Руководство пользователя", command=self._show_help)

    def _show_about(self):
        """Показывает информацию о программе"""
        about_text = """
        Система учета и бронирования VR-оборудования

        Версия: 1.0

        Программа предназначена для учета и бронирования VR-оборудования 
        в образовательной организации.

        © 2025 Все права защищены
        """

        messagebox.showinfo("О программе", about_text)

    def _show_data_generator(self):
        """Открывает окно генерации тестовых данных"""
        show_generator_dialog(self, self.db)

    def _create_widgets(self):
        """Создание всех виджетов приложения"""
        # Создаем главный контейнер с отступами
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок приложения
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(
            header_frame,
            text="Система учета и бронирования VR-оборудования",
            font=("Segoe UI", 18, "bold"),
            foreground="#3498db"
        ).pack(side=tk.LEFT)

        # Информация о дате и времени
        self.datetime_label = ttk.Label(header_frame, text="", font=("Segoe UI", 10))
        self.datetime_label.pack(side=tk.RIGHT, padx=5)
        self._update_datetime()

        # Создаем вкладки
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        # Вкладка "Оборудование"
        self.equipment_frame = EquipmentFrame(self.notebook, self.db)
        self.notebook.add(self.equipment_frame, text="Оборудование")

        # Вкладка "Бронирование"
        self.booking_frame = BookingFrame(self.notebook, self.db)
        self.notebook.add(self.booking_frame, text="Бронирование")

        # Статусная строка
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(
            status_frame,
            text="© 2025 Система учета и бронирования VR-оборудования образовательной организации",
            font=("Segoe UI", 8)
        ).pack(side=tk.LEFT)

        # Кнопка справки
        ttk.Button(
            status_frame,
            text="Справка",
            command=self._show_help,
            width=10
        ).pack(side=tk.RIGHT, padx=5)

    def _update_datetime(self):
        """Обновляет информацию о текущей дате и времени"""
        now = datetime.now()
        current_datetime = now.strftime("%d.%m.%Y %H:%M:%S")
        self.datetime_label.config(text=f"Текущая дата и время: {current_datetime}")

        # Обновляем каждую секунду
        self.after(1000, self._update_datetime)

    def _show_help(self):
        """Показывает справочную информацию"""
        help_text = """
        Система учета и бронирования VR-оборудования

        Раздел "Оборудование":
        - Добавление, редактирование и удаление VR-оборудования
        - Просмотр информации о бронировании оборудования

        Раздел "Бронирование":
        - Бронирование оборудования на определенную дату и время
        - Указание кабинета и ответственного лица
        - Управление существующими бронированиями

        Дополнительные функции:
        - Генерация тестовых данных доступна через меню "Инструменты" -> "Генерация тестовых данных"
        - Справочная информация доступна через меню "Справка" -> "Руководство пользователя"
        - Информация о программе доступна через меню "Файл" -> "О программе"

        Для добавления оборудования или бронирования используйте соответствующие кнопки в верхней части экрана.
        Для редактирования или удаления - дважды кликните по нужной записи или используйте контекстное меню (правая кнопка мыши).
        """

        # Создаем окно помощи
        help_window = tk.Toplevel(self)
        help_window.title("Справка")
        help_window.geometry("600x400")
        help_window.resizable(True, True)

        # Делаем окно модальным
        help_window.grab_set()

        # Создаем текстовый виджет со скроллбаром
        text_frame = ttk.Frame(help_window, padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Segoe UI", 11))
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Связываем скроллбар с текстовым виджетом
        scrollbar.config(command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)

        # Вставляем текст справки
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)  # Запрещаем редактирование

        # Кнопка закрытия
        ttk.Button(
            help_window,
            text="Закрыть",
            command=help_window.destroy,
            width=10
        ).pack(pady=10)

    def _on_close(self):
        """Обработчик закрытия приложения"""
        # Закрываем соединение с базой данных
        if hasattr(self, 'db'):
            self.db.close()

        # Закрываем приложение
        self.destroy()


if __name__ == "__main__":
    app = VREquipmentApp()
    app.mainloop()
