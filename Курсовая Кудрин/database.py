import sqlite3
import os
from datetime import datetime


class Database:
    """Класс для работы с базой данных SQLite"""

    def __init__(self, db_name="vr_equipment.db"):
        """Инициализация соединения с базой данных"""
        # Создаем базу в текущей директории
        self.db_path = os.path.join(os.getcwd(), db_name)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Создание необходимых таблиц в базе данных, если они не существуют"""
        # Таблица оборудования
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model TEXT NOT NULL,
            serial_number TEXT,
            description TEXT,
            purchase_date TEXT,
            status TEXT DEFAULT 'Доступно'
        )
        ''')

        # Таблица бронирования
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS booking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            room TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            booked_by TEXT,
            notes TEXT,
            FOREIGN KEY (equipment_id) REFERENCES equipment (id) ON DELETE CASCADE
        )
        ''')

        self.conn.commit()

    # Методы для работы с оборудованием
    def add_equipment(self, name, model, serial_number="", description="", purchase_date=""):
        """Добавление нового оборудования в базу данных"""
        try:
            self.cursor.execute(
                "INSERT INTO equipment (name, model, serial_number, description, purchase_date) VALUES (?, ?, ?, ?, ?)",
                (name, model, serial_number, description, purchase_date)
            )
            self.conn.commit()
            return True, self.cursor.lastrowid
        except sqlite3.Error as e:
            return False, str(e)

    def update_equipment(self, equipment_id, name, model, serial_number="", description="", purchase_date="",
                         status="Доступно"):
        """Обновление информации об оборудовании"""
        try:
            self.cursor.execute(
                """UPDATE equipment 
                   SET name=?, model=?, serial_number=?, description=?, purchase_date=?, status=? 
                   WHERE id=?""",
                (name, model, serial_number, description, purchase_date, status, equipment_id)
            )
            self.conn.commit()
            return True, None
        except sqlite3.Error as e:
            return False, str(e)

    def delete_equipment(self, equipment_id):
        """Удаление оборудования из базы данных"""
        try:
            # Проверяем, есть ли активные бронирования для этого оборудования
            self.cursor.execute(
                """SELECT COUNT(*) FROM booking 
                   WHERE equipment_id=? AND date(booking_date) >= date('now')""",
                (equipment_id,)
            )
            active_bookings = self.cursor.fetchone()[0]

            if active_bookings > 0:
                return False, "Невозможно удалить оборудование с активными бронированиями"

            self.cursor.execute("DELETE FROM equipment WHERE id=?", (equipment_id,))
            self.conn.commit()
            return True, None
        except sqlite3.Error as e:
            return False, str(e)

    def get_all_equipment(self):
        """Получение всего списка оборудования"""
        try:
            self.cursor.execute("SELECT id, name, model, serial_number, status FROM equipment ORDER BY name")
            return True, self.cursor.fetchall()
        except sqlite3.Error as e:
            return False, str(e)

    def get_equipment_details(self, equipment_id):
        """Получение подробной информации об оборудовании"""
        try:
            self.cursor.execute("SELECT * FROM equipment WHERE id=?", (equipment_id,))
            return True, self.cursor.fetchone()
        except sqlite3.Error as e:
            return False, str(e)

    def get_available_equipment(self, booking_date, start_time, end_time):
        """Получение доступного оборудования на указанную дату и время"""
        try:
            self.cursor.execute("""
                SELECT id, name, model, serial_number, status 
                FROM equipment 
                WHERE status = 'Доступно' 
                AND id NOT IN (
                    SELECT equipment_id FROM booking 
                    WHERE booking_date = ? 
                    AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
                )
                ORDER BY name
            """, (booking_date, start_time, start_time, end_time, end_time))
            return True, self.cursor.fetchall()
        except sqlite3.Error as e:
            return False, str(e)

    # Методы для работы с бронированием
    def add_booking(self, equipment_id, booking_date, start_time, end_time, room, booked_by="", notes=""):
        """Добавление нового бронирования"""
        try:
            # Проверяем, доступно ли оборудование на указанное время
            self.cursor.execute("""
                SELECT COUNT(*) FROM booking 
                WHERE equipment_id = ? 
                AND booking_date = ? 
                AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
            """, (equipment_id, booking_date, start_time, start_time, end_time, end_time))

            if self.cursor.fetchone()[0] > 0:
                return False, "Оборудование уже забронировано на указанное время"

            # Если оборудование доступно, создаем бронирование
            self.cursor.execute(
                """INSERT INTO booking 
                   (equipment_id, booking_date, start_time, end_time, room, booked_by, notes, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (equipment_id, booking_date, start_time, end_time, room, booked_by, notes,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            self.conn.commit()
            return True, self.cursor.lastrowid
        except sqlite3.Error as e:
            return False, str(e)

    def update_booking(self, booking_id, equipment_id, booking_date, start_time, end_time, room, booked_by="",
                       notes=""):
        """Обновление информации о бронировании"""
        try:
            # Проверяем, доступно ли оборудование на указанное время (исключая текущее бронирование)
            self.cursor.execute("""
                SELECT COUNT(*) FROM booking 
                WHERE equipment_id = ? 
                AND booking_date = ? 
                AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
                AND id != ?
            """, (equipment_id, booking_date, start_time, start_time, end_time, end_time, booking_id))

            if self.cursor.fetchone()[0] > 0:
                return False, "Оборудование уже забронировано на указанное время"

            self.cursor.execute(
                """UPDATE booking 
                   SET equipment_id=?, booking_date=?, start_time=?, end_time=?, room=?, booked_by=?, notes=? 
                   WHERE id=?""",
                (equipment_id, booking_date, start_time, end_time, room, booked_by, notes, booking_id)
            )
            self.conn.commit()
            return True, None
        except sqlite3.Error as e:
            return False, str(e)

    def delete_booking(self, booking_id):
        """Удаление бронирования"""
        try:
            self.cursor.execute("DELETE FROM booking WHERE id=?", (booking_id,))
            self.conn.commit()
            return True, None
        except sqlite3.Error as e:
            return False, str(e)

    def get_all_bookings(self):
        """Получение всех бронирований с информацией об оборудовании"""
        try:
            self.cursor.execute("""
                SELECT b.id, e.name, e.model, b.booking_date, b.start_time, b.end_time, b.room, b.booked_by
                FROM booking b
                JOIN equipment e ON b.equipment_id = e.id
                ORDER BY b.booking_date DESC, b.start_time
            """)
            return True, self.cursor.fetchall()
        except sqlite3.Error as e:
            return False, str(e)

    def get_booking_details(self, booking_id):
        """Получение подробной информации о бронировании"""
        try:
            self.cursor.execute("""
                SELECT b.*, e.name, e.model
                FROM booking b
                JOIN equipment e ON b.equipment_id = e.id
                WHERE b.id=?
            """, (booking_id,))
            return True, self.cursor.fetchone()
        except sqlite3.Error as e:
            return False, str(e)

    def get_equipment_bookings(self, equipment_id):
        """Получение всех бронирований для конкретного оборудования"""
        try:
            self.cursor.execute("""
                SELECT id, booking_date, start_time, end_time, room, booked_by
                FROM booking
                WHERE equipment_id=?
                ORDER BY booking_date DESC, start_time
            """, (equipment_id,))
            return True, self.cursor.fetchall()
        except sqlite3.Error as e:
            return False, str(e)

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
