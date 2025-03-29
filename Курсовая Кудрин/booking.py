import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime

class BookingFrame(ttk.Frame):
    """Класс для отображения и управления разделом 'Бронирование'"""
    
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        
        # Создаем и размещаем элементы интерфейса
        self._create_widgets()
        
        # Загружаем данные при инициализации
        self.load_booking_data()
    
    def _create_widgets(self):
        """Создает все виджеты для раздела бронирования"""
        # Верхняя панель с кнопками управления
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Заголовок раздела
        ttk.Label(
            control_frame, 
            text="Бронирование VR-оборудования", 
            style="Header.TLabel"
        ).pack(side=tk.LEFT, padx=5)
        
        # Кнопки управления
        ttk.Button(
            control_frame, 
            text="Забронировать оборудование", 
            command=self.open_add_booking_window,
            style="Action.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            control_frame, 
            text="Обновить", 
            command=self.load_booking_data,
            style="TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        # Фильтры
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр по дате:").pack(side=tk.LEFT, padx=5)
        
        # Фильтр по дате
        self.date_filter_var = tk.StringVar(value="Все даты")
        date_filter = ttk.Combobox(
            filter_frame, 
            textvariable=self.date_filter_var, 
            values=["Все даты", "Сегодня", "Будущие", "Прошедшие", "Выбрать..."], 
            width=15
        )
        date_filter.pack(side=tk.LEFT, padx=5)
        date_filter.bind("<<ComboboxSelected>>", self.on_date_filter_change)
        
        # Календарь для выбора даты (изначально скрыт)
        self.calendar_frame = ttk.Frame(filter_frame)
        self.calendar = DateEntry(
            self.calendar_frame, 
            width=12, 
            locale='ru_RU', 
            date_pattern='dd.MM.yyyy'
        )
        self.calendar.pack(side=tk.LEFT)
        
        ttk.Button(
            self.calendar_frame, 
            text="Применить", 
            command=self.apply_date_filter,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Поиск
        ttk.Label(filter_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_booking_list())
        ttk.Entry(
            filter_frame, 
            textvariable=self.search_var, 
            width=30
        ).pack(side=tk.LEFT, padx=5)
        
        # Основная таблица со списком бронирований
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создаем Treeview для отображения данных бронирований
        columns = ('id', 'equipment', 'model', 'date', 'start_time', 'end_time', 'room', 'booked_by')
        self.booking_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show='headings', 
            selectmode='browse'
        )
        
        # Устанавливаем заголовки столбцов
        self.booking_tree.heading('id', text='ID')
        self.booking_tree.heading('equipment', text='Оборудование')
        self.booking_tree.heading('model', text='Модель')
        self.booking_tree.heading('date', text='Дата')
        self.booking_tree.heading('start_time', text='Начало')
        self.booking_tree.heading('end_time', text='Окончание')
        self.booking_tree.heading('room', text='Кабинет')
        self.booking_tree.heading('booked_by', text='Кем забронировано')
        
        # Настраиваем ширину столбцов
        self.booking_tree.column('id', width=50, anchor='center')
        self.booking_tree.column('equipment', width=150)
        self.booking_tree.column('model', width=150)
        self.booking_tree.column('date', width=100, anchor='center')
        self.booking_tree.column('start_time', width=80, anchor='center')
        self.booking_tree.column('end_time', width=80, anchor='center')
        self.booking_tree.column('room', width=80, anchor='center')
        self.booking_tree.column('booked_by', width=150)
        
        # Привязываем двойной клик к открытию окна редактирования
        self.booking_tree.bind('<Double-1>', self.on_booking_double_click)
        
        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.booking_tree.yview)
        self.booking_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.booking_tree.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем контекстное меню
        self.context_menu = tk.Menu(self.booking_tree, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.edit_selected_booking)
        self.context_menu.add_command(label="Удалить", command=self.delete_selected_booking)
        
        # Привязываем правую кнопку мыши к вызову контекстного меню
        self.booking_tree.bind("<Button-3>", self.show_context_menu)
        
        # Информация внизу
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(info_frame, text="Всего бронирований: 0")
        self.status_label.pack(side=tk.LEFT, padx=5)
    
    def load_booking_data(self):
        """Загружает данные о бронированиях из базы данных"""
        # Очищаем таблицу
        for i in self.booking_tree.get_children():
            self.booking_tree.delete(i)
        
        # Загружаем данные
        success, data = self.db.get_all_bookings()
        
        if success:
            # Заполняем таблицу данными
            self._fill_booking_tree(data)
        else:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {data}")
    
    def _fill_booking_tree(self, data):
        """Заполняет дерево бронирований данными с учетом фильтров"""
        # Очищаем таблицу
        for i in self.booking_tree.get_children():
            self.booking_tree.delete(i)
        
        # Получаем текущую дату для сравнения
        today = datetime.datetime.now().date()
        
        # Применяем фильтр по дате
        filtered_data = []
        date_filter = self.date_filter_var.get()
        
        for booking in data:
            booking_id, equipment_name, equipment_model, booking_date, start_time, end_time, room, booked_by = booking
            
            # Преобразуем строку даты в объект datetime
            try:
                booking_date_parts = booking_date.split('.')
                if len(booking_date_parts) == 3:
                    day, month, year = map(int, booking_date_parts)
                    booking_date_obj = datetime.date(year, month, day)
                elif booking_date.count('-') == 2:
                    year, month, day = map(int, booking_date.split('-'))
                    booking_date_obj = datetime.date(year, month, day)
                else:
                    booking_date_obj = today  # Если не удалось распознать формат
            except Exception:
                booking_date_obj = today  # Если возникла ошибка при преобразовании даты
            
            # Применяем фильтр
            include_booking = True
            
            if date_filter == "Сегодня":
                include_booking = booking_date_obj == today
            elif date_filter == "Будущие":
                include_booking = booking_date_obj >= today
            elif date_filter == "Прошедшие":
                include_booking = booking_date_obj < today
            elif date_filter == "Выбрать...":
                selected_date = self.calendar.get_date()
                include_booking = booking_date_obj == selected_date
            
            # Применяем поиск
            search_text = self.search_var.get().lower()
            if search_text:
                search_matched = False
                for value in booking:
                    if search_text in str(value).lower():
                        search_matched = True
                        break
                include_booking = include_booking and search_matched
            
            if include_booking:
                filtered_data.append(booking)
                
                # Определяем, прошло ли бронирование
                is_past = booking_date_obj < today
                
                # Добавляем строку с тегом, если бронирование прошло
                item = self.booking_tree.insert('', 'end', values=booking)
                if is_past:
                    self.booking_tree.item(item, tags=('past',))
        
        # Настраиваем тег для прошедших бронирований
        self.booking_tree.tag_configure('past', foreground='gray')
        
        # Обновляем информацию о количестве
        self.status_label.config(text=f"Показано бронирований: {len(filtered_data)} из {len(data)}")
    
    def filter_booking_list(self):
        """Фильтрует список бронирований по введенному тексту и выбранной дате"""
        # Загружаем данные и применяем фильтры
        success, data = self.db.get_all_bookings()
        
        if success:
            self._fill_booking_tree(data)
        else:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {data}")
    
    def on_date_filter_change(self, event):
        """Обработчик изменения фильтра по дате"""
        if self.date_filter_var.get() == "Выбрать...":
            # Показываем календарь
            self.calendar_frame.pack(side=tk.LEFT, padx=5)
        else:
            # Скрываем календарь
            self.calendar_frame.pack_forget()
            # Применяем фильтр сразу
            self.filter_booking_list()
    
    def apply_date_filter(self):
        """Применяет фильтр по выбранной в календаре дате"""
        self.filter_booking_list()
    
    def open_add_booking_window(self):
        """Открывает окно для добавления нового бронирования"""
        booking_window = BookingWindow(self, self.db)
        booking_window.grab_set()  # Делаем окно модальным
    
    def edit_selected_booking(self):
        """Открывает окно редактирования выбранного бронирования"""
        selected_item = self.booking_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для редактирования")
            return
        
        # Получаем ID выбранного бронирования
        booking_id = self.booking_tree.item(selected_item[0], 'values')[0]
        
        # Получаем данные о бронировании из базы
        success, booking_data = self.db.get_booking_details(booking_id)
        
        if success:
            # Открываем окно редактирования
            booking_window = BookingWindow(self, self.db, booking_data)
            booking_window.grab_set()  # Делаем окно модальным
        else:
            messagebox.showerror("Ошибка", f"Не удалось получить данные: {booking_data}")
    
    def on_booking_double_click(self, event):
        """Обработчик двойного клика по элементу списка"""
        self.edit_selected_booking()
    
    def delete_selected_booking(self):
        """Удаляет выбранное бронирование"""
        selected_item = self.booking_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для удаления")
            return
        
        # Получаем ID выбранного бронирования
        booking_id = self.booking_tree.item(selected_item[0], 'values')[0]
        equipment_name = self.booking_tree.item(selected_item[0], 'values')[1]
        
        # Спрашиваем подтверждение
        if messagebox.askyesno("Подтверждение", f"Вы действительно хотите удалить бронирование оборудования '{equipment_name}'?"):
            # Удаляем бронирование из базы
            success, error_message = self.db.delete_booking(booking_id)
            
            if success:
                messagebox.showinfo("Успех", "Бронирование успешно удалено")
                self.load_booking_data()  # Перезагружаем данные
            else:
                messagebox.showerror("Ошибка", f"Не удалось удалить бронирование: {error_message}")
    
    def show_context_menu(self, event):
        """Показывает контекстное меню при нажатии правой кнопки мыши"""
        # Убеждаемся, что под курсором есть элемент
        item = self.booking_tree.identify_row(event.y)
        if item:
            # Выбираем элемент под курсором
            self.booking_tree.selection_set(item)
            # Показываем контекстное меню
            self.context_menu.post(event.x_root, event.y_root)


class BookingWindow(tk.Toplevel):
    """Окно для добавления или редактирования бронирования"""
    
    def __init__(self, parent, db, booking_data=None):
        super().__init__(parent)
        
        self.parent = parent
        self.db = db
        self.booking_data = booking_data
        
        # Настраиваем окно
        self.title("Бронирование оборудования" if not booking_data else "Редактирование бронирования")
        self.geometry("550x550")
        self.resizable(False, False)
        
        # Создаем все виджеты
        self._create_widgets()
        
        # Если передано бронирование для редактирования, заполняем поля
        if booking_data:
            self._fill_booking_data()
    
    def _create_widgets(self):
        """Создает все виджеты окна"""
        form_frame = ttk.Frame(self, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(
            form_frame, 
            text="Бронирование VR-оборудования", 
            style="Header.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Дата бронирования
        ttk.Label(form_frame, text="Дата бронирования*:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.booking_date = DateEntry(form_frame, width=20, locale='ru_RU', date_pattern='dd.MM.yyyy')
        self.booking_date.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        self.booking_date.bind("<<DateEntrySelected>>", self.refresh_available_equipment)
        
        # Время начала
        ttk.Label(form_frame, text="Время начала*:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        time_frame_start = ttk.Frame(form_frame)
        time_frame_start.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.start_hour_var = tk.StringVar(value="08")
        self.start_minute_var = tk.StringVar(value="00")
        
        hours = [f"{i:02d}" for i in range(8, 21)]  # От 8:00 до 20:00
        minutes = ["00", "15", "30", "45"]
        
        ttk.Combobox(
            time_frame_start, 
            textvariable=self.start_hour_var, 
            values=hours, 
            width=5, 
            state="readonly"
        ).pack(side=tk.LEFT)
        
        ttk.Label(time_frame_start, text=":").pack(side=tk.LEFT)
        
        ttk.Combobox(
            time_frame_start, 
            textvariable=self.start_minute_var, 
            values=minutes, 
            width=5, 
            state="readonly"
        ).pack(side=tk.LEFT)
        
        # Кнопка обновления доступного оборудования
        ttk.Button(
            time_frame_start, 
            text="Обновить список", 
            command=self.refresh_available_equipment
        ).pack(side=tk.LEFT, padx=10)
        
        # Время окончания
        ttk.Label(form_frame, text="Время окончания*:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        time_frame_end = ttk.Frame(form_frame)
        time_frame_end.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.end_hour_var = tk.StringVar(value="09")
        self.end_minute_var = tk.StringVar(value="00")
        
        ttk.Combobox(
            time_frame_end, 
            textvariable=self.end_hour_var, 
            values=hours, 
            width=5, 
            state="readonly"
        ).pack(side=tk.LEFT)
        
        ttk.Label(time_frame_end, text=":").pack(side=tk.LEFT)
        
        ttk.Combobox(
            time_frame_end, 
            textvariable=self.end_minute_var, 
            values=minutes, 
            width=5, 
            state="readonly"
        ).pack(side=tk.LEFT)
        
        # Оборудование
        ttk.Label(form_frame, text="Оборудование*:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        
        # Создаем фрейм для списка оборудования
        equipment_frame = ttk.Frame(form_frame)
        equipment_frame.grid(row=4, column=1, rowspan=2, pady=5, padx=5, sticky=tk.W + tk.E + tk.N + tk.S)
        
        # Добавляем полосу прокрутки
        equipment_scrollbar = ttk.Scrollbar(equipment_frame)
        equipment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Список доступного оборудования
        self.equipment_listbox = tk.Listbox(
            equipment_frame, 
            height=6, 
            width=40, 
            selectmode=tk.SINGLE,
            yscrollcommand=equipment_scrollbar.set
        )
        self.equipment_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        equipment_scrollbar.config(command=self.equipment_listbox.yview)
        
        # Кабинет
        ttk.Label(form_frame, text="Кабинет*:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=5)
        self.room_var = tk.StringVar()
        rooms = ["101", "102", "103", "201", "202", "203", "301", "302", "303", "Спортзал", "Актовый зал", "Другое"]
        room_combo = ttk.Combobox(form_frame, textvariable=self.room_var, values=rooms, width=25)
        room_combo.grid(row=6, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Кем забронировано
        ttk.Label(form_frame, text="Кем забронировано:").grid(row=7, column=0, sticky=tk.W, pady=5, padx=5)
        self.booked_by_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.booked_by_var, width=40).grid(row=7, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Примечания
        ttk.Label(form_frame, text="Примечания:").grid(row=8, column=0, sticky=tk.W + tk.N, pady=5, padx=5)
        self.notes_text = tk.Text(form_frame, width=40, height=5)
        self.notes_text.grid(row=8, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Информация об обязательных полях
        ttk.Label(form_frame, text="* - обязательные поля", font=('Segoe UI', 8)).grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=10, padx=5)
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            button_frame,
            text="Сохранить",
            style="Success.TButton",
            command=self.save_booking,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Отмена",
            style="Cancel.TButton",
            command=self.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Загружаем доступное оборудование
        self.refresh_available_equipment()
    
    def refresh_available_equipment(self, event=None):
        """Обновляет список доступного оборудования на выбранную дату и время"""
        booking_date = self.booking_date.get_date().strftime("%d.%m.%Y")
        start_time = f"{self.start_hour_var.get()}:{self.start_minute_var.get()}"
        end_time = f"{self.end_hour_var.get()}:{self.end_minute_var.get()}"
        
        # Проверка корректности времени
        try:
            start_hour, start_minute = map(int, self.start_hour_var.get()), map(int, self.start_minute_var.get())
            end_hour, end_minute = map(int, self.end_hour_var.get()), map(int, self.end_minute_var.get())
            
            if int(self.start_hour_var.get()) > int(self.end_hour_var.get()) or (
                int(self.start_hour_var.get()) == int(self.end_hour_var.get()) and 
                int(self.start_minute_var.get()) >= int(self.end_minute_var.get())
            ):
                messagebox.showwarning("Предупреждение", "Время окончания должно быть позже времени начала")
                return
        except ValueError:
            messagebox.showwarning("Предупреждение", "Некорректное время")
            return
        
        # Сохраняем текущий выбор (ID оборудования)
        current_selection = None
        if self.booking_data:  # Для режима редактирования
            current_selection = self.booking_data[1]  # ID оборудования
        
        # Очищаем список
        self.equipment_listbox.delete(0, tk.END)
        
        # Получаем доступное оборудование
        success, equipment_list = self.db.get_available_equipment(booking_date, start_time, end_time)
        
        if success:
            self.equipment_ids = []  # Сохраняем ID оборудования
            
            for item in equipment_list:
                equipment_id, name, model, serial, status = item
                self.equipment_ids.append(equipment_id)
                self.equipment_listbox.insert(tk.END, f"{name} - {model}")
                
            # Если редактируем существующее бронирование, то добавляем текущее оборудование
            if self.booking_data and not current_selection in self.equipment_ids:
                # Получаем данные текущего оборудования
                _, current_equipment_id, _, _, _, _, _, _, _, equipment_name, equipment_model = self.booking_data
                
                # Добавляем в список и выбираем
                self.equipment_listbox.insert(0, f"{equipment_name} - {equipment_model} (текущий выбор)")
                self.equipment_ids.insert(0, current_equipment_id)
                self.equipment_listbox.selection_set(0)
            
            # Если список пуст
            if not equipment_list and not (self.booking_data and current_selection):
                self.equipment_listbox.insert(tk.END, "Нет доступного оборудования на выбранное время")
                self.equipment_ids = []
        else:
            messagebox.showerror("Ошибка", f"Не удалось получить список оборудования: {equipment_list}")
    
    def _fill_booking_data(self):
        """Заполняет форму данными для редактирования"""
        if not self.booking_data:
            return
        
        # Распаковываем данные бронирования
        booking_id, equipment_id, booking_date, start_time, end_time, room, created_at, booked_by, notes, equipment_name, equipment_model = self.booking_data
        
        # Устанавливаем дату
        try:
            # Преобразуем строку даты в объект datetime
            date_parts = booking_date.split('.')
            if len(date_parts) == 3:
                day, month, year = map(int, date_parts)
                self.booking_date.set_date(datetime.datetime(year, month, day))
            else:
                # Если формат не DD.MM.YYYY, пробуем другие форматы
                try:
                    date_obj = datetime.datetime.strptime(booking_date, "%Y-%m-%d")
                    self.booking_date.set_date(date_obj)
                except ValueError:
                    # Если не удалось распознать формат, оставляем текущую дату
                    pass
        except Exception:
            # Если возникла ошибка при установке даты, оставляем текущую
            pass
        
        # Устанавливаем время начала
        try:
            start_hour, start_minute = start_time.split(':')
            self.start_hour_var.set(start_hour)
            self.start_minute_var.set(start_minute)
        except:
            # Если возникла ошибка, оставляем стандартные значения
            pass
        
        # Устанавливаем время окончания
        try:
            end_hour, end_minute = end_time.split(':')
            self.end_hour_var.set(end_hour)
            self.end_minute_var.set(end_minute)
        except:
            # Если возникла ошибка, оставляем стандартные значения
            pass
        
        # Загружаем доступное оборудование (с учетом текущего выбора)
        self.refresh_available_equipment()
        
        # Устанавливаем кабинет
        self.room_var.set(room if room else "")
        
        # Устанавливаем информацию о том, кто забронировал
        self.booked_by_var.set(booked_by if booked_by else "")
        
        # Устанавливаем примечания
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, notes if notes else "")
    
    def save_booking(self):
        """Сохраняет данные о бронировании в базу"""
        # Получаем данные из формы
        booking_date = self.booking_date.get_date().strftime("%d.%m.%Y")
        start_time = f"{self.start_hour_var.get()}:{self.start_minute_var.get()}"
        end_time = f"{self.end_hour_var.get()}:{self.end_minute_var.get()}"
        room = self.room_var.get().strip()
        booked_by = self.booked_by_var.get().strip()
        notes = self.notes_text.get(1.0, tk.END).strip()
        
        # Проверяем обязательные поля
        if not room:
            messagebox.showwarning("Предупреждение", "Пожалуйста, укажите кабинет")
            return
        
        # Проверяем, что выбрано оборудование
        selected_index = self.equipment_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите оборудование")
            return
        
        try:
            equipment_id = self.equipment_ids[selected_index[0]]
        except IndexError:
            messagebox.showwarning("Предупреждение", "Невозможно определить выбранное оборудование")
            return
        
        # Проверяем корректность времени
        try:
            if int(self.start_hour_var.get()) > int(self.end_hour_var.get()) or (
                int(self.start_hour_var.get()) == int(self.end_hour_var.get()) and 
                int(self.start_minute_var.get()) >= int(self.end_minute_var.get())
            ):
                messagebox.showwarning("Предупреждение", "Время окончания должно быть позже времени начала")
                return
        except ValueError:
            messagebox.showwarning("Предупреждение", "Некорректное время")
            return
        
        # Сохраняем данные в зависимости от режима (добавление или редактирование)
        if not self.booking_data:
            # Добавление нового бронирования
            success, result = self.db.add_booking(
                equipment_id, booking_date, start_time, end_time, room, booked_by, notes
            )
            
            if success:
                messagebox.showinfo("Успех", "Оборудование успешно забронировано")
                self.parent.load_booking_data()  # Обновляем данные в родительском окне
                self.destroy()  # Закрываем окно
            else:
                messagebox.showerror("Ошибка", f"Не удалось забронировать оборудование: {result}")
        else:
            # Редактирование существующего бронирования
            booking_id = self.booking_data[0]
            success, error_message = self.db.update_booking(
                booking_id, equipment_id, booking_date, start_time, end_time, room, booked_by, notes
            )
            
            if success:
                messagebox.showinfo("Успех", "Бронирование успешно обновлено")
                self.parent.load_booking_data()  # Обновляем данные в родительском окне
                self.destroy()  # Закрываем окно
            else:
                messagebox.showerror("Ошибка", f"Не удалось обновить бронирование: {error_message}")
