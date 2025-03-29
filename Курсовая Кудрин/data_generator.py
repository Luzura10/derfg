"""
Модуль генерации случайных данных для базы данных VR-оборудования
"""
import random
import sqlite3
import datetime
from tkinter import messagebox
import tkinter as tk
from database import Database

class DataGenerator:
    """Класс для генерации случайных данных"""

    # Списки для генерации случайных значений
    vr_names = [
        "Oculus Quest", "HTC Vive", "Valve Index", "PlayStation VR",
        "HP Reverb G2", "Samsung Gear VR", "Varjo VR-3", "Pico Neo",
        "Windows Mixed Reality", "Pimax Vision", "Lenovo Explorer"
    ]

    vr_models = [
        "Pro", "Elite", "Standard", "Lite", "Enterprise", "Educational",
        "Gaming Edition", "Business Edition", "X2", "V3", "Next Gen"
    ]

    descriptions = [
        "Полностью автономная VR-гарнитура с высоким разрешением",
        "Профессиональная VR-система с поддержкой отслеживания движений",
        "Бюджетная модель для образовательных целей",
        "VR-гарнитура с высокой частотой обновления экрана",
        "Компактная VR-система с встроенными наушниками",
        "Беспроводная VR-гарнитура с контроллерами 6DoF",
        "Система виртуальной реальности с поддержкой трекинга глаз",
        "VR-гарнитура с улучшенной графической производительностью",
        "Специализированная система для образовательных учреждений",
        "VR-система с расширенным полем зрения",
        "Гарнитура с максимальным погружением и поддержкой жестов"
    ]

    rooms = ["Кабинет A-101", "Лаборатория B-202", "Класс C-303", "Конференц-зал D-404",
             "Медиацентр E-505", "Учебная аудитория F-121", "Мультимедийный класс G-222",
             "Лекционная аудитория H-323", "Компьютерный класс I-424", "Образовательный центр J-525"]

    users = ["Иванов И.И.", "Петров П.П.", "Сидоров С.С.", "Козлова К.К.", "Николаева Н.Н.",
             "Александров А.А.", "Михайлов М.М.", "Федоров Ф.Ф.", "Волкова В.В.", "Кузнецов К.К.",
             "Соколова С.С.", "Павлов П.П.", "Семенов С.С.", "Голубева Г.Г.", "Виноградов В.В."]

    notes = ["Для проведения урока по 3D-моделированию",
             "Демонстрация виртуальной лаборатории",
             "Практическое занятие по VR-разработке",
             "Обучение новым технологиям",
             "Презентация образовательного контента",
             "Для курса 'Основы виртуальной реальности'",
             "Внеклассное мероприятие",
             "Методическое занятие для преподавателей",
             "Исследовательский проект учащихся",
             "Открытый урок с использованием VR-технологий"]

    def __init__(self, db):
        """Инициализация генератора данных"""
        self.db = db

    def generate_random_equipment(self, count=10):
        """Генерирует случайное оборудование"""
        for _ in range(count):
            name = random.choice(self.vr_names)
            model = random.choice(self.vr_models)
            serial_number = f"SN-{random.randint(10000, 99999)}"
            description = random.choice(self.descriptions)

            # Генерация случайной даты покупки за последние 5 лет
            days_back = random.randint(0, 5*365)
            purchase_date = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%d.%m.%Y")

            # Добавление оборудования в базу данных
            try:
                success, result = self.db.add_equipment(name, model, serial_number, description, purchase_date)
                if not success:
                    print(f"Ошибка при добавлении оборудования: {result}")
            except sqlite3.Error as e:
                print(f"Ошибка при добавлении оборудования: {e}")

    def generate_random_bookings(self, count=20):
        """Генерирует случайные бронирования"""
        # Получаем список всего оборудования
        success, equipment_list = self.db.get_all_equipment()

        if not success or not equipment_list:
            print("Не удалось получить список оборудования")
            return False

        # Проверяем, что equipment_list не пустой список и содержит корректные данные
        if not isinstance(equipment_list, list) or len(equipment_list) == 0:
            print("Список оборудования пуст или имеет неверный формат")
            return False

        # Проверяем структуру данных оборудования
        for item in equipment_list:
            if not isinstance(item, tuple) or len(item) < 1:
                print(f"Некорректный формат данных оборудования: {item}")
                return False

        for _ in range(count):
            # Выбираем случайное оборудование
            equipment = random.choice(equipment_list)

            # Проверяем формат данных оборудования
            if isinstance(equipment, tuple) and len(equipment) > 0:
                equipment_id = equipment[0]  # ID оборудования
            else:
                print(f"Некорректный формат данных: {equipment}")
                continue  # Пропускаем этот элемент

            # Генерация случайной даты бронирования (от сегодня до +30 дней)
            days_ahead = random.randint(0, 30)
            booking_date = (datetime.datetime.now() + datetime.timedelta(days=days_ahead)).strftime("%d.%m.%Y")

            # Генерация случайного времени (часы работы учреждения 8:00 - 18:00)
            start_hour = random.randint(8, 16)
            duration = random.randint(1, 2)  # Длительность 1-2 часа
            end_hour = min(start_hour + duration, 18)

            start_time = f"{start_hour:02d}:00"
            end_time = f"{end_hour:02d}:00"

            room = random.choice(self.rooms)
            booked_by = random.choice(self.users)
            notes = random.choice(self.notes)

            # Добавление бронирования в базу данных
            try:
                success, result = self.db.add_booking(equipment_id, booking_date, start_time, end_time, room, booked_by, notes)
                if not success:
                    print(f"Ошибка при добавлении бронирования: {result}")
            except sqlite3.Error as e:
                print(f"Ошибка при добавлении бронирования: {e}")

        return True


def show_generator_dialog(parent, db):
    """Показывает диалоговое окно для генерации тестовых данных"""
    dialog = tk.Toplevel(parent)
    dialog.title("Генерация тестовых данных")
    dialog.geometry("400x250")
    dialog.resizable(False, False)
    dialog.grab_set()  # Блокирует взаимодействие с родительским окном

    # Устанавливаем значки
    try:
        dialog.iconbitmap("icon.ico")
    except:
        pass

    # Фрейм для контента
    content_frame = tk.Frame(dialog, padx=20, pady=20)
    content_frame.pack(fill=tk.BOTH, expand=True)

    # Заголовок
    header_label = tk.Label(
        content_frame,
        text="Генерация тестовых данных",
        font=("Arial", 14, "bold")
    )
    header_label.pack(pady=(0, 15))

    # Описание
    description_label = tk.Label(
        content_frame,
        text="Укажите количество случайных записей для генерации:",
        font=("Arial", 10),
        wraplength=350,
        justify=tk.LEFT
    )
    description_label.pack(anchor=tk.W, pady=(0, 10))

    # Фрейм для ввода количества оборудования
    equipment_frame = tk.Frame(content_frame)
    equipment_frame.pack(fill=tk.X, pady=5)

    equipment_label = tk.Label(equipment_frame, text="Оборудование:", width=15, anchor=tk.W)
    equipment_label.pack(side=tk.LEFT)

    equipment_var = tk.StringVar(value="10")
    equipment_entry = tk.Entry(equipment_frame, textvariable=equipment_var, width=5)
    equipment_entry.pack(side=tk.LEFT)

    # Фрейм для ввода количества бронирований
    booking_frame = tk.Frame(content_frame)
    booking_frame.pack(fill=tk.X, pady=5)

    booking_label = tk.Label(booking_frame, text="Бронирования:", width=15, anchor=tk.W)
    booking_label.pack(side=tk.LEFT)

    booking_var = tk.StringVar(value="20")
    booking_entry = tk.Entry(booking_frame, textvariable=booking_var, width=5)
    booking_entry.pack(side=tk.LEFT)

    # Фрейм для кнопок
    button_frame = tk.Frame(content_frame)
    button_frame.pack(fill=tk.X, pady=(20, 0))

    def on_generate():
        try:
            equipment_count = int(equipment_var.get())
            booking_count = int(booking_var.get())

            if equipment_count <= 0 or booking_count <= 0:
                messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
                return

            # Генерируем данные
            generator = DataGenerator(db)
            generator.generate_random_equipment(equipment_count)

            # Генерируем бронирования только если есть оборудование
            booking_result = generator.generate_random_bookings(booking_count)

            # Показываем сообщение об успехе
            messagebox.showinfo(
                "Успешно",
                f"Данные успешно сгенерированы:\n"
                f"• Оборудование: {equipment_count} шт.\n"
                f"• Бронирования: {'успешно добавлены' if booking_result else 'не добавлены (нет оборудования)'}"
            )

            # Закрываем окно
            dialog.destroy()

            # Обновляем данные в основном приложении
            if hasattr(parent, "equipment_frame") and hasattr(parent.equipment_frame, "load_equipment_data"):
                parent.equipment_frame.load_equipment_data()

            if hasattr(parent, "booking_frame") and hasattr(parent.booking_frame, "load_booking_data"):
                parent.booking_frame.load_booking_data()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")

    # Кнопка генерации
    generate_button = tk.Button(
        button_frame,
        text="Сгенерировать",
        command=on_generate,
        bg="#4CAF50",
        fg="black",
        font=("Arial", 10, "bold"),
        padx=10
    )
    generate_button.pack(side=tk.RIGHT, padx=5)

    # Кнопка отмены
    cancel_button = tk.Button(
        button_frame,
        text="Отмена",
        command=dialog.destroy,
        bg="#f1f1f1",
        fg="black",
        font=("Arial", 10),
        padx=10
    )
    cancel_button.pack(side=tk.RIGHT, padx=5)

    # Центрируем диалог относительно родительского окна
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")