import unittest
from database import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Создаем тестовую базу данных в памяти
        self.db = Database(":memory:")

    def test_add_equipment(self):
        # Тестируем добавление оборудования
        success, equipment_id = self.db.add_equipment(
            "Test VR", "Test Model", "SN12345", "Test Description", "01.01.2023"
        )
        self.assertTrue(success)
        self.assertIsInstance(equipment_id, int)

    def test_get_equipment(self):
        # Тестируем получение информации об оборудовании
        self.db.add_equipment("Test VR", "Test Model", "SN12345", "Test Description", "01.01.2023")
        success, result = self.db.get_all_equipment()
        self.assertTrue(success)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Test VR")

    def tearDown(self):
        # Закрываем соединение с тестовой базой данных
        self.db.close()


if __name__ == '__main__':
    unittest.main()