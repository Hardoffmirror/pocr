#!/usr/bin/env python3
"""
Тест импорта предметов из текста игры
"""

from item_parser import ItemParser


def test_russian_ring():
    """Тест импорта кольца на русском"""
    print("=" * 80)
    print("ТЕСТ 1: Импорт кольца (русский язык)")
    print("=" * 80)

    text = """
Класс предмета: Кольца
Редкость: Редкий
Громадный захват
Кольцо без камня
--------
Требования:
Уровень: 67
--------
Гнезда: R
--------
Уровень предмета: 86
--------
Имеет 1 гнездо (implicit)
--------
+29% к сопротивлению хаосу (fractured)
+37 к максимуму энергетического щита
28% повышение редкости найденных предметов
+14% к сопротивлению всем стихиям
+48% к сопротивлению холоду
--------
Расколотый предмет
--------
Примечание: ~b/o 2 chaos
    """

    parser = ItemParser()
    item = parser.parse_item_text(text)

    if item:
        print("✓ Успешно распарсено!\n")
        print(item)
        print(f"\nСтатистика:")
        print(f"  Префиксов: {item.prefix_count}")
        print(f"  Суффиксов: {item.suffix_count}")
        print(f"  Fractured: {'Да' if item.has_fractured_mod() else 'Нет'}")
        print(f"  Corrupted: {'Да' if item.is_corrupted else 'Нет'}")
    else:
        print("✗ Ошибка парсинга!")

    print()


def test_weapon():
    """Тест импорта оружия"""
    print("=" * 80)
    print("ТЕСТ 2: Импорт меча")
    print("=" * 80)

    text = """
Класс предмета: Мечи
Редкость: Редкий
Смертельный клинок
Королевский меч
--------
Уровень предмета: 85
--------
+100 к максимуму здоровья
+50% к физическому урону
+30% к скорости атаки
+40% к шансу критического удара
+35% к сопротивлению огню
    """

    parser = ItemParser()
    item = parser.parse_item_text(text)

    if item:
        print("✓ Успешно распарсено!\n")
        print(item)
        print(f"\nСтатистика:")
        print(f"  Префиксов: {item.prefix_count}")
        print(f"  Суффиксов: {item.suffix_count}")
    else:
        print("✗ Ошибка парсинга!")

    print()


def test_armour():
    """Тест импорта доспеха"""
    print("=" * 80)
    print("ТЕСТ 3: Импорт доспеха")
    print("=" * 80)

    text = """
Класс предмета: Нагрудные доспехи
Редкость: Редкий
Некротические доспехи
Уровень предмета: 86
--------
+90 к максимуму здоровья
+45% к энергетическому щиту
+40% к уклонению
+35% к подавлению заклинаний
+50 к интеллекту
--------
    """

    parser = ItemParser()
    item = parser.parse_item_text(text)

    if item:
        print("✓ Успешно распарсено!\n")
        print(item)
        print(f"\nСтатистика:")
        print(f"  Префиксов: {item.prefix_count}")
        print(f"  Суффиксов: {item.suffix_count}")
    else:
        print("✗ Ошибка парсинга!")

    print()


def main():
    """Запуск всех тестов"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 25 + "ТЕСТ ИМПОРТА ПРЕДМЕТОВ" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    test_russian_ring()
    test_weapon()
    test_armour()

    print("=" * 80)
    print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 80)
    print("\nТеперь вы можете использовать эту же функцию в GUI!")
    print("Запустите: python main.py")
    print()


if __name__ == "__main__":
    main()
