import unittest
import time
from superhero.function import find_tallest_hero


class TestFindTallestHeroRealAPI(unittest.TestCase):
    REQUEST_DELAY = 1

    def setUp(self):
        time.sleep(self.REQUEST_DELAY)

    def validate_hero(self, result, gender, has_job):
        """Общая валидация результатов для валидных героев"""
        self.assertIsInstance(result, dict, "Результат должен быть словарем с данными героя")

        # Проверка пола
        hero_gender = str(result['appearance']['gender']).strip().lower()
        self.assertEqual(hero_gender, gender.strip().lower(), "Пол героя не соответствует запрошенному")

        # Проверка занятости
        occupation = str(result['work'].get('occupation', '')).lower()
        unemployed_indicators = [
            "unemployed", "no known occupation", "none", "-", "n/a",
            "retired", "without job", "no job", "not employed", "without employment"
        ]

        if has_job:
            self.assertTrue(occupation, "У работающего героя должно быть указано занятие")
            self.assertFalse(
                any(ind in occupation for ind in unemployed_indicators),
                "Работающий герой не должен иметь индикаторов безработицы"
            )
        else:
            self.assertTrue(
                not occupation or any(ind in occupation for ind in unemployed_indicators),
                "Безработный герой должен иметь индикаторы безработицы"
            )

        # Проверка роста
        height_data = result['appearance']['height']
        self.assertIsInstance(height_data, list, "Данные о росте должны быть списком")
        self.assertGreaterEqual(len(height_data), 2, "Должны быть указаны метрическая и имперская системы")

        height_str = str(height_data[1])
        self.assertTrue(height_str.endswith(' cm'), "Рост должен быть в сантиметрах")

        try:
            height_cm = float(height_str.replace(' cm', '').strip())
            self.assertGreater(height_cm, 100, "Рост должен быть больше 100 см")
        except ValueError:
            self.fail(f"Невозможно преобразовать рост в число: {height_str}")

    # 1. Тест: Поиск работающего мужчины
    def test_employed_male(self):
        """Тест: поиск работающего мужчины"""
        result = find_tallest_hero("Male", True)
        self.validate_hero(result, "Male", True)
        print(f"\nСамый высокий работающий мужчина: {result['name']}, Рост: {result['appearance']['height'][1]}")

    # 2. Тест: Поиск безработного мужчины
    def test_unemployed_male(self):
        """Тест: поиск безработного мужчины"""
        result = find_tallest_hero("Male", False)
        self.validate_hero(result, "Male", False)
        print(f"\nСамый высокий безработный мужчина: {result['name']}, Рост: {result['appearance']['height'][1]}")

    # 3. Тест: Поиск работающей женщины
    def test_employed_female(self):
        """Тест: поиск работающей женщины"""
        result = find_tallest_hero("Female", True)
        self.validate_hero(result, "Female", True)
        print(f"\nСамый высокий работающая женщина: {result['name']}, Рост: {result['appearance']['height'][1]}")

    # 4. Тест: Поиск безработной женщины
    def test_unemployed_female(self):
        """Тест: поиск безработной женщины"""
        result = find_tallest_hero("Female", False)
        self.validate_hero(result, "Female", False)
        print(f"\nСамый высокий безработная женщина: {result['name']}, Рост: {result['appearance']['height'][1]}")

    # 5. Тест: Валидные спецсимволы в поле пола
    def test_valid_special_characters(self):
        """Тест: валидные спецсимволы в поле пола"""
        test_cases = [
            ("  Male  ", True),  # Пробелы
            ("\tFemale\t", True),  # Табуляция
            ("Male\n", True),  # Перенос строки
        ]

        for gender, has_job in test_cases:
            with self.subTest(gender=gender, has_job=has_job):
                result = find_tallest_hero(gender, has_job)
                self.assertIsInstance(result, dict, "Должен вернуться словарь с героем")
                self.validate_hero(result, gender, has_job)

    # 6. Тест: Невалидные спецсимволы в поле пола
    def test_invalid_special_characters(self):
        """Тест: невалидные спецсимволы в поле пола (кириллица)"""
        test_cases = [
            ("Mаle", True),  # Кириллическая 'а'
            ("Fеmale", True),  # Кириллическая 'е'
            ("Mаlе", True),  # Кириллические 'а' и 'е'
        ]

        for gender, has_job in test_cases:
            with self.subTest(gender=gender, has_job=has_job):
                result = find_tallest_hero(gender, has_job)
                self.assertEqual(result, "Герои не найдены")

    # 7. Тест: Пустые значения параметров
    def test_empty_values(self):
        """Тест: пустые значения параметров"""
        # Кейс 1: Пустая строка для gender
        result = find_tallest_hero("", True)
        self.assertEqual(result, "Герои не найдены")

        # Кейс 2: None для gender
        with self.assertRaises(TypeError):
            find_tallest_hero(None, True)

        # Кейс 3: None для has_job
        with self.assertRaises(TypeError):
            find_tallest_hero("Male", None)

        # Кейс 4: None для обоих параметров
        with self.assertRaises(TypeError):
            find_tallest_hero(None, None)

    # 8. Тест: Экстремальные значения параметров
    def test_extreme_parameters(self):
        """Тест: экстремальные значения параметров"""
        # Кейс 1: Длинная строка (1000 символов)
        result = find_tallest_hero("A" * 1000, True)
        self.assertEqual(result, "Герои не найдены")

        # Кейс 2: Короткая строка (1 символ)
        result = find_tallest_hero("M", True)
        self.assertEqual(result, "Герои не найдены")

        # Кейс 3: Числовое значение для has_job
        with self.assertRaises(TypeError):
            find_tallest_hero("Male", 1)

        # Кейс 4: Строковое значение для has_job
        with self.assertRaises(TypeError):
            find_tallest_hero("Female", "True")

        # Кейс 5: Нулевое значение для has_job
        with self.assertRaises(TypeError):
            find_tallest_hero("Female", 0)

        # Кейс 6: Коллекция для has_job
        with self.assertRaises(TypeError):
            find_tallest_hero("Male", [])


if __name__ == '__main__':
    unittest.main(verbosity=2)