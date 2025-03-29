"""
Модуль с стилями и настройками интерфейса для приложения
"""

# Основные цвета
PRIMARY_COLOR = "#2563eb"  # Основной цвет (яркий синий)
SECONDARY_COLOR = "#1e40af"  # Вторичный цвет (насыщенный темно-синий)
ACCENT_COLOR = "#dc2626"  # Акцентный цвет (яркий красный)
BG_COLOR = "#f5f5f5"  # Фоновый цвет (светло-серый)
TEXT_COLOR = "#1a1a1a"  # Цвет текста (почти черный)
SUCCESS_COLOR = "#16a34a"  # Цвет успеха (насыщенный зеленый)
WARNING_COLOR = "#ea580c"  # Цвет предупреждения (яркий оранжевый)
LIGHT_GREY = "#e2e8f0"  # Светло-серый для второстепенных элементов

# Шрифты
FONT_FAMILY = "Segoe UI"  # Основной шрифт
FONT_SIZE_SMALL = 10
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 14
FONT_SIZE_HEADER = 16
FONT_SIZE_TITLE = 18

# Отступы и размеры
PADDING_SMALL = 5
PADDING_NORMAL = 10
PADDING_LARGE = 15
BUTTON_WIDTH_SMALL = 8
BUTTON_WIDTH_NORMAL = 12
BUTTON_WIDTH_LARGE = 15

# Стили для ttk
def configure_styles(style):
    """Настраивает стили для ttk элементов"""
    # Основной стиль для кнопок
    style.configure(
        'TButton',
        font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
        background=PRIMARY_COLOR,
        foreground='black',  # Меняем цвет текста на черный
        padding=7,
        borderwidth=2
    )

    # Добавляем эффект при наведении и нажатии для всех кнопок
    style.map('TButton',
        background=[('active', SECONDARY_COLOR), ('pressed', SECONDARY_COLOR)],
        relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
    )

    # Кнопка действия (синяя)
    style.configure(
        'Action.TButton',
        background=PRIMARY_COLOR,
        foreground='black',  # Черный текст
        font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold')
    )

    # Эффект при наведении для кнопки действия
    style.map('Action.TButton',
        background=[('active', SECONDARY_COLOR), ('pressed', SECONDARY_COLOR)],
        foreground=[('active', 'black'), ('pressed', 'black')],  # Сохраняем черный при наведении
        relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
    )

    # Кнопка удаления (красная)
    style.configure(
        'Delete.TButton',
        background=ACCENT_COLOR,
        foreground='black',  # Черный текст
        font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold')
    )

    # Эффект при наведении для кнопки удаления
    style.map('Delete.TButton',
        background=[('active', '#b91c1c'), ('pressed', '#b91c1c')],
        foreground=[('active', 'black'), ('pressed', 'black')],  # Сохраняем черный при наведении
        relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
    )

    # Кнопка отмены (серая)
    style.configure(
        'Cancel.TButton',
        background=LIGHT_GREY,
        foreground='black',  # Черный текст
        font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold')
    )

    # Эффект при наведении для кнопки отмены
    style.map('Cancel.TButton',
        background=[('active', '#cbd5e1'), ('pressed', '#cbd5e1')],
        foreground=[('active', 'black'), ('pressed', 'black')],  # Сохраняем черный при наведении
        relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
    )

    # Кнопка успеха (зеленая)
    style.configure(
        'Success.TButton',
        background=SUCCESS_COLOR,
        foreground='black',  # Черный текст
        font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold')
    )

    # Эффект при наведении для кнопки успеха
    style.map('Success.TButton',
        background=[('active', '#15803d'), ('pressed', '#15803d')],
        foreground=[('active', 'black'), ('pressed', 'black')],  # Сохраняем черный при наведении
        relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
    )

    # Заголовки
    style.configure(
        'Header.TLabel',
        font=(FONT_FAMILY, FONT_SIZE_HEADER, 'bold'),
        foreground=TEXT_COLOR,
        background=BG_COLOR,
        padding=10
    )

    # Подзаголовки
    style.configure(
        'Subheader.TLabel',
        font=(FONT_FAMILY, FONT_SIZE_LARGE, 'bold'),
        foreground=TEXT_COLOR,
        background=BG_COLOR,
        padding=5
    )

    # Обычный текст
    style.configure(
        'TLabel',
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        foreground=TEXT_COLOR,
        background=BG_COLOR
    )

    # Поля ввода
    style.configure(
        'TEntry',
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        fieldbackground='white'
    )

    # Комбобокс
    style.configure(
        'TCombobox',
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        background='white'
    )

    # Рамки
    style.configure(
        'TFrame',
        background=BG_COLOR
    )

    # Вкладки
    style.configure(
        'TNotebook',
        background=BG_COLOR,
        tabmargins=[2, 5, 2, 0]
    )

    style.configure(
        'TNotebook.Tab',
        font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),  # Делаем шрифт жирным
        padding=[15, 8],  # Увеличиваем отступы
        background=LIGHT_GREY,
        foreground=TEXT_COLOR,
        borderwidth=2  # Добавляем обводку
    )

    style.map('TNotebook.Tab',
        background=[('selected', PRIMARY_COLOR), ('active', SECONDARY_COLOR)],  # Добавляем эффект при наведении
        foreground=[('selected', 'black'), ('active', 'black')],  # Черный текст при наведении
        expand=[('selected', [1, 1, 1, 0])]  # Немного увеличиваем активную вкладку
    )

    # Стиль для TreeView (таблиц)
    style.configure(
        'Treeview',
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        background='white',
        foreground=TEXT_COLOR,
        rowheight=30,  # Увеличиваем высоту строк
        borderwidth=1
    )

    # Добавляем эффект выделения строки
    style.map('Treeview',
        background=[('selected', '#dbeafe')],  # Светло-синий фон для выделенной строки
        foreground=[('selected', '#1e40af')]   # Темно-синий текст для выделенной строки
    )

    style.configure(
        'Treeview.Heading',
        font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
        background=PRIMARY_COLOR,  # Используем основной цвет для заголовков
        foreground='black',       # Черный текст в заголовках
        relief='raised',          # Рельефный стиль для заголовков
        borderwidth=1             # Тонкая граница
    )
    
    # Стиль для радиокнопок и чекбоксов
    style.configure(
        'TCheckbutton',
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        background=BG_COLOR,
        foreground=TEXT_COLOR
    )
    
    style.configure(
        'TRadiobutton',
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        background=BG_COLOR,
        foreground=TEXT_COLOR
    )

# Функция для создания всплывающих сообщений
def message_box_config():
    """Возвращает словарь с конфигурацией для messagebox"""
    return {
        "font": (FONT_FAMILY, FONT_SIZE_NORMAL),
        "background": BG_COLOR,
        "foreground": TEXT_COLOR
    }
