import requests


def find_tallest_hero(gender, has_job):
    # Проверка типов параметров
    if not isinstance(gender, str):
        raise TypeError("gender должен быть строкой")
    if not isinstance(has_job, bool):
        raise TypeError("has_job должен быть булевым значением")

    # Очистка и нормализация пола
    gender = gender.strip().lower()

    try:
        response = requests.get('https://akabab.github.io/superhero-api/api/all.json', timeout=10)
        response.raise_for_status()
        heroes = response.json()
    except requests.RequestException:
        return "Ошибка: не удалось загрузить данные"

    candidates = []

    unemployed_indicators = [
        "unemployed", "no known occupation", "none", "-", "n/a",
        "retired", "without job", "no job", "not employed", "without employment"
    ]

    for hero in heroes:
        # Безопасная обработка appearance
        appearance = hero.get('appearance', {})
        if not isinstance(appearance, dict):
            continue

        # Проверка и нормализация пола
        hero_gender = str(appearance.get('gender', '')).strip().lower()
        if hero_gender != gender:
            continue

        # Безопасная обработка work
        work = hero.get('work', {})
        occupation = str(work.get('occupation', '')).lower() if isinstance(work, dict) else ""

        if has_job:
            if not occupation or any(ind in occupation for ind in unemployed_indicators):
                continue
        else:
            if occupation and not any(ind in occupation for ind in unemployed_indicators):
                continue

        # Обработка роста
        height_data = appearance.get('height', [])
        if not isinstance(height_data, list) or len(height_data) < 2:
            continue

        height_str = str(height_data[1])
        if not height_str.endswith(' cm'):
            continue

        try:
            height_cm = float(height_str.replace(' cm', '').strip())
            if height_cm <= 100:  # Игнорировать нереалистичный рост
                continue
        except (ValueError, TypeError):
            continue

        candidates.append((hero, height_cm))

    if not candidates:
        return "Герои не найдены"

    tallest_hero = max(candidates, key=lambda x: x[1])
    return tallest_hero[0]