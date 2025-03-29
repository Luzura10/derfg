import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime

class EquipmentFrame(ttk.Frame):
    """Класс для отображения и управления разделом 'Оборудование'"""
    
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        
        # Создаем и размещаем элементы интерфейса
        self._create_widgets()
        
        # Загружаем данные при инициализации
        self.load_equipment_data()
    
    def _create_widgets(self):
        """Создает все виджеты для раздела оборудования"""
        # Верхняя панель с кнопками управления
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Заголовок раздела
        ttk.Label(
            control_frame, 
            text="Управление VR-оборудованием", 
            style="Header.TLabel"
        ).pack(side=tk.LEFT, padx=5)
        
        # Кнопки управления
        ttk.Button(
            control_frame, 
            text="Добавить оборудование", 
            command=self.open_add_equipment_window,
            style="Action.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            control_frame, 
            text="Обновить", 
            command=self.load_equipment_data,
            style="TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        # Рамка для поиска
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_equipment_list())
        ttk.Entry(
            search_frame, 
            textvariable=self.search_var, 
            width=40
        ).pack(side=tk.LEFT, padx=5)
        
        # Основная таблица со списком оборудования
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создаем Treeview для отображения данных оборудования
        columns = ('id', 'name', 'model', 'serial_number', 'status')
        self.equipment_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show='headings', 
            selectmode='browse'
        )
        
        # Устанавливаем заголовки столбцов
        self.equipment_tree.heading('id', text='ID')
        self.equipment_tree.heading('name', text='Название')
        self.equipment_tree.heading('model', text='Модель')
        self.equipment_tree.heading('serial_number', text='Серийный номер')
        self.equipment_tree.heading('status', text='Статус')
        
        # Настраиваем ширину столбцов
        self.equipment_tree.column('id', width=50, anchor='center')
        self.equipment_tree.column('name', width=200)
        self.equipment_tree.column('model', width=200)
        self.equipment_tree.column('serial_number', width=150)
        self.equipment_tree.column('status', width=100, anchor='center')
        
        # Привязываем двойной клик к открытию окна редактирования
        self.equipment_tree.bind('<Double-1>', self.on_equipment_double_click)
        
        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.equipment_tree.yview)
        self.equipment_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.equipment_tree.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем контекстное меню
        self.context_menu = tk.Menu(self.equipment_tree, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.edit_selected_equipment)
        self.context_menu.add_command(label="Удалить", command=self.delete_selected_equipment)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Просмотреть бронирования", command=self.view_bookings)
        
        # Привязываем правую кнопку мыши к вызову контекстного меню
        self.equipment_tree.bind("<Button-3>", self.show_context_menu)
        
        # Информация внизу
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(info_frame, text="Всего оборудования: 0")
        self.status_label.pack(side=tk.LEFT, padx=5)
    
    def load_equipment_data(self):
        """Загружает данные об оборудовании из базы данных"""
        # Очищаем таблицу
        for i in self.equipment_tree.get_children():
            self.equipment_tree.delete(i)
        
        # Загружаем данные
        success, data = self.db.get_all_equipment()
        
        if success:
            # Заполняем таблицу данными
            for item in data:
                self.equipment_tree.insert('', 'end', values=item)
            
            # Обновляем информацию о количестве
            self.status_label.config(text=f"Всего оборудования: {len(data)}")
        else:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {data}")
    
    def filter_equipment_list(self):
        """Фильтрует список оборудования по введенному тексту"""
        search_text = self.search_var.get().lower()
        
        # Очищаем таблицу
        for i in self.equipment_tree.get_children():
            self.equipment_tree.delete(i)
        
        # Загружаем данные
        success, data = self.db.get_all_equipment()
        
        if success:
            # Фильтруем и заполняем таблицу данными
            filtered_data = []
            for item in data:
                # Преобразуем все значения в строки и проверяем вхождение текста поиска
                if any(search_text in str(value).lower() for value in item):
                    self.equipment_tree.insert('', 'end', values=item)
                    filtered_data.append(item)
            
            # Обновляем информацию о количестве
            self.status_label.config(text=f"Найдено оборудования: {len(filtered_data)} из {len(data)}")
        else:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {data}")
    
    def open_add_equipment_window(self):
        """Открывает окно для добавления нового оборудования"""
        equipment_window = EquipmentWindow(self, self.db)
        equipment_window.grab_set()  # Делаем окно модальным
    
    def edit_selected_equipment(self):
        """Открывает окно редактирования выбранного оборудования"""
        selected_item = self.equipment_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите оборудование для редактирования")
            return
        
        # Получаем ID выбранного оборудования
        equipment_id = self.equipment_tree.item(selected_item[0], 'values')[0]
        
        # Получаем данные об оборудовании из базы
        success, equipment_data = self.db.get_equipment_details(equipment_id)
        
        if success:
            # Открываем окно редактирования
            equipment_window = EquipmentWindow(self, self.db, equipment_data)
            equipment_window.grab_set()  # Делаем окно модальным
        else:
            messagebox.showerror("Ошибка", f"Не удалось получить данные: {equipment_data}")
    
    def on_equipment_double_click(self, event):
        """Обработчик двойного клика по элементу списка"""
        self.edit_selected_equipment()
    
    def delete_selected_equipment(self):
        """Удаляет выбранное оборудование"""
        selected_item = self.equipment_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите оборудование для удаления")
            return
        
        # Получаем ID выбранного оборудования
        equipment_id = self.equipment_tree.item(selected_item[0], 'values')[0]
        equipment_name = self.equipment_tree.item(selected_item[0], 'values')[1]
        
        # Спрашиваем подтверждение
        if messagebox.askyesno("Подтверждение", f"Вы действительно хотите удалить оборудование '{equipment_name}'?"):
            # Удаляем оборудование из базы
            success, error_message = self.db.delete_equipment(equipment_id)
            
            if success:
                messagebox.showinfo("Успех", "Оборудование успешно удалено")
                self.load_equipment_data()  # Перезагружаем данные
            else:
                messagebox.showerror("Ошибка", f"Не удалось удалить оборудование: {error_message}")
    
    def view_bookings(self):
        """Открывает окно для просмотра бронирований выбранного оборудования"""
        selected_item = self.equipment_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите оборудование для просмотра бронирований")
            return
        
        # Получаем ID выбранного оборудования
        equipment_id = self.equipment_tree.item(selected_item[0], 'values')[0]
        equipment_name = self.equipment_tree.item(selected_item[0], 'values')[1]
        
        # Получаем данные о бронированиях из базы
        success, bookings_data = self.db.get_equipment_bookings(equipment_id)
        
        if success:
            # Открываем окно с бронированиями
            booking_window = EquipmentBookingsWindow(self, equipment_id, equipment_name, bookings_data)
            booking_window.grab_set()  # Делаем окно модальным
        else:
            messagebox.showerror("Ошибка", f"Не удалось получить данные о бронированиях: {bookings_data}")
    
    def show_context_menu(self, event):
        """Показывает контекстное меню при нажатии правой кнопки мыши"""
        # Убеждаемся, что под курсором есть элемент
        item = self.equipment_tree.identify_row(event.y)
        if item:
            # Выбираем элемент под курсором
            self.equipment_tree.selection_set(item)
            # Показываем контекстное меню
            self.context_menu.post(event.x_root, event.y_root)


class EquipmentWindow(tk.Toplevel):
    """Окно для добавления или редактирования оборудования"""
    
    def __init__(self, parent, db, equipment_data=None):
        super().__init__(parent)
        
        self.parent = parent
        self.db = db
        self.equipment_data = equipment_data
        
        # Настраиваем окно
        self.title("Добавление оборудования" if not equipment_data else "Редактирование оборудования")
        self.geometry("500x450")
        self.resizable(False, False)
        
        # Создаем все виджеты
        self._create_widgets()
        
        # Если передано оборудование для редактирования, заполняем поля
        if equipment_data:
            self._fill_equipment_data()
    
    def _create_widgets(self):
        """Создает все виджеты окна"""
        form_frame = ttk.Frame(self, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Название
        ttk.Label(form_frame, text="Название*:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Модель
        ttk.Label(form_frame, text="Модель*:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.model_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.model_var, width=40).grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Серийный номер
        ttk.Label(form_frame, text="Серийный номер:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.serial_number_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.serial_number_var, width=40).grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=3, column=0, sticky=tk.W + tk.N, pady=5, padx=5)
        self.description_text = tk.Text(form_frame, width=40, height=5)
        self.description_text.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Дата приобретения
        ttk.Label(form_frame, text="Дата приобретения:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        self.purchase_date = DateEntry(form_frame, width=20, locale='ru_RU', date_pattern='dd.MM.yyyy')
        self.purchase_date.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Статус (только для редактирования)
        ttk.Label(form_frame, text="Статус:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        self.status_var = tk.StringVar(value="Доступно")
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var, width=20, values=["Доступно", "Недоступно", "В ремонте"])
        status_combo.grid(row=5, column=1, pady=5, padx=5, sticky=tk.W)
        status_combo.state(['readonly'])  # Делаем поле только для чтения
        
        # Информация об обязательных полях
        ttk.Label(form_frame, text="* - обязательные поля", font=('Segoe UI', 8)).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=10, padx=5)
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            button_frame,
            text="Сохранить",
            style="Success.TButton",
            command=self.save_equipment,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Отмена",
            style="Cancel.TButton",
            command=self.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def _fill_equipment_data(self):
        """Заполняет форму данными для редактирования"""
        if not self.equipment_data:
            return
        
        # Распаковываем данные оборудования
        id, name, model, serial_number, description, purchase_date, status = self.equipment_data
        
        # Заполняем поля
        self.name_var.set(name)
        self.model_var.set(model)
        self.serial_number_var.set(serial_number if serial_number else "")
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, description if description else "")
        
        # Устанавливаем дату
        if purchase_date:
            try:
                # Преобразуем строку даты в объект datetime
                date_parts = purchase_date.split('.')
                if len(date_parts) == 3:
                    day, month, year = map(int, date_parts)
                    self.purchase_date.set_date(datetime.datetime(year, month, day))
                else:
                    # Если формат не DD.MM.YYYY, пробуем другие форматы
                    try:
                        date_obj = datetime.datetime.strptime(purchase_date, "%Y-%m-%d")
                        self.purchase_date.set_date(date_obj)
                    except ValueError:
                        # Если не удалось распознать формат, оставляем текущую дату
                        pass
            except Exception:
                # Если возникла ошибка при установке даты, оставляем текущую
                pass
        
        # Устанавливаем статус
        self.status_var.set(status if status else "Доступно")
    
    def save_equipment(self):
        """Сохраняет данные об оборудовании в базу"""
        # Получаем данные из формы
        name = self.name_var.get().strip()
        model = self.model_var.get().strip()
        serial_number = self.serial_number_var.get().strip()
        description = self.description_text.get(1.0, tk.END).strip()
        purchase_date = self.purchase_date.get_date().strftime("%d.%m.%Y")
        status = self.status_var.get()
        
        # Проверяем обязательные поля
        if not name or not model:
            messagebox.showwarning("Предупреждение", "Пожалуйста, заполните обязательные поля")
            return
        
        # Сохраняем данные в зависимости от режима (добавление или редактирование)
        if not self.equipment_data:
            # Добавление нового оборудования
            success, result = self.db.add_equipment(name, model, serial_number, description, purchase_date)
            
            if success:
                messagebox.showinfo("Успех", "Оборудование успешно добавлено")
                self.parent.load_equipment_data()  # Обновляем данные в родительском окне
                self.destroy()  # Закрываем окно
            else:
                messagebox.showerror("Ошибка", f"Не удалось добавить оборудование: {result}")
        else:
            # Редактирование существующего оборудования
            equipment_id = self.equipment_data[0]
            success, error_message = self.db.update_equipment(
                equipment_id, name, model, serial_number, description, purchase_date, status
            )
            
            if success:
                messagebox.showinfo("Успех", "Оборудование успешно обновлено")
                self.parent.load_equipment_data()  # Обновляем данные в родительском окне
                self.destroy()  # Закрываем окно
            else:
                messagebox.showerror("Ошибка", f"Не удалось обновить оборудование: {error_message}")


class EquipmentBookingsWindow(tk.Toplevel):
    """Окно для просмотра бронирований оборудования"""
    
    def __init__(self, parent, equipment_id, equipment_name, bookings_data):
        super().__init__(parent)
        
        self.parent = parent
        self.equipment_id = equipment_id
        self.equipment_name = equipment_name
        self.bookings_data = bookings_data
        
        # Настраиваем окно
        self.title(f"Бронирования для '{equipment_name}'")
        self.geometry("700x400")
        self.resizable(True, True)
        
        # Создаем виджеты
        self._create_widgets()
    
    def _create_widgets(self):
        """Создает виджеты для окна просмотра бронирований"""
        # Заголовок
        title_frame = ttk.Frame(self, padding=10)
        title_frame.pack(fill=tk.X)
        
        ttk.Label(
            title_frame, 
            text=f"Бронирования для оборудования: {self.equipment_name}", 
            style="Header.TLabel"
        ).pack(anchor=tk.W)
        
        # Основная таблица бронирований
        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем Treeview для отображения бронирований
        columns = ('id', 'date', 'start_time', 'end_time', 'room', 'booked_by')
        self.bookings_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show='headings', 
            selectmode='browse'
        )
        
        # Устанавливаем заголовки столбцов
        self.bookings_tree.heading('id', text='ID')
        self.bookings_tree.heading('date', text='Дата')
        self.bookings_tree.heading('start_time', text='Начало')
        self.bookings_tree.heading('end_time', text='Окончание')
        self.bookings_tree.heading('room', text='Кабинет')
        self.bookings_tree.heading('booked_by', text='Кем забронировано')
        
        # Настраиваем ширину столбцов
        self.bookings_tree.column('id', width=50, anchor='center')
        self.bookings_tree.column('date', width=100, anchor='center')
        self.bookings_tree.column('start_time', width=80, anchor='center')
        self.bookings_tree.column('end_time', width=80, anchor='center')
        self.bookings_tree.column('room', width=100, anchor='center')
        self.bookings_tree.column('booked_by', width=200)
        
        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bookings_tree.pack(fill=tk.BOTH, expand=True)
        
        # Заполняем таблицу данными
        self._fill_bookings_data()
        
        # Кнопка закрытия
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Закрыть",
            command=self.destroy,
            width=15
        ).pack(side=tk.RIGHT, padx=5)
    
    def _fill_bookings_data(self):
        """Заполняет таблицу данными о бронированиях"""
        # Очищаем таблицу
        for i in self.bookings_tree.get_children():
            self.bookings_tree.delete(i)
        
        # Заполняем таблицу данными
        if self.bookings_data:
            today = datetime.datetime.now().date()
            
            for booking in self.bookings_data:
                booking_id, booking_date, start_time, end_time, room, booked_by = booking
                
                # Проверяем, прошло ли бронирование
                is_past = False
                try:
                    # Преобразуем строку даты в объект datetime
                    booking_date_parts = booking_date.split('.')
                    if len(booking_date_parts) == 3:
                        day, month, year = map(int, booking_date_parts)
                        booking_date_obj = datetime.date(year, month, day)
                    elif booking_date.count('-') == 2:
                        year, month, day = map(int, booking_date.split('-'))
                        booking_date_obj = datetime.date(year, month, day)
                    else:
                        booking_date_obj = today  # Если не удалось распознать формат
                    
                    is_past = booking_date_obj < today
                except Exception:
                    pass  # Если возникла ошибка при преобразовании даты
                
                # Добавляем данные с соответствующим стилем (серый для прошедших бронирований)
                item = self.bookings_tree.insert('', 'end', values=(
                    booking_id, booking_date, start_time, end_time, room, booked_by if booked_by else "Не указано"
                ))
                
                if is_past:
                    self.bookings_tree.item(item, tags=('past',))
            
            # Настраиваем тег для прошедших бронирований
            self.bookings_tree.tag_configure('past', foreground='gray')
