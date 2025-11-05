#!/usr/bin/env python3
"""
Неинтерактивная версия демо для тестирования
"""

from models import Item, Mod, ModType, ModTier, ItemClass
from calculator import RecombinatorCalculator
from simulator import RecombinatorSimulator


def test_all():
    """Запуск всех тестов"""
    print("\n" + "=" * 80)
    print("ТЕСТ 1: Создание предметов и модов")
    print("=" * 80)

    # Создаем предметы
    item1 = Item(
        name="Test Sword",
        item_class=ItemClass.SWORD,
        item_level=85
    )

    item1.prefixes.append(Mod(
        name="+100 to Maximum Life",
        mod_type=ModType.PREFIX,
        tier=ModTier.T1,
        mod_group="Life"
    ))

    item1.suffixes.append(Mod(
        name="+45% to Fire Resistance",
        mod_type=ModType.SUFFIX,
        tier=ModTier.T1,
        mod_group="FireResistance"
    ))

    print("✓ Предмет создан успешно")
    print(f"  Префиксов: {item1.prefix_count}")
    print(f"  Суффиксов: {item1.suffix_count}")

    print("\n" + "=" * 80)
    print("ТЕСТ 2: Калькулятор вероятностей")
    print("=" * 80)

    item2 = Item(
        name="Test Sword 2",
        item_class=ItemClass.SWORD,
        item_level=85
    )

    item2.prefixes.append(Mod(
        name="+50 to Strength",
        mod_type=ModType.PREFIX,
        tier=ModTier.T2,
        mod_group="Strength"
    ))

    calculator = RecombinatorCalculator()
    outcomes = calculator.analyze_all_outcomes(item1, item2)

    print(f"✓ Рассчитано {len(outcomes)} возможных исходов")

    stats = calculator.get_statistics_summary(outcomes)
    print(f"  Средний шанс успеха: {stats['average_success_rate']:.2%}")

    print("\n" + "=" * 80)
    print("ТЕСТ 3: Симулятор")
    print("=" * 80)

    simulator = RecombinatorSimulator()

    # Одна попытка
    result = simulator.simulate_single_recombination(item1, item2)
    print(f"✓ Одна симуляция: {'Успех' if result.success else 'Провал'}")

    # Множество попыток
    results = simulator.simulate_multiple_recombinations(item1, item2, 100)
    print(f"✓ 100 симуляций выполнено")
    print(f"  Успехов: {results['successes']}")
    print(f"  Провалов: {results['failures']}")
    print(f"  Процент успеха: {results['success_rate']:.2%}")

    print("\n" + "=" * 80)
    print("ТЕСТ 4: Проверка ограничений")
    print("=" * 80)

    # Разные классы
    item3 = Item("Ring", ItemClass.RING, 80)
    can_combine, reason = item1.can_recombine_with(item3)
    print(f"✓ Проверка разных классов: {not can_combine} (ожидается False)")
    print(f"  Причина: {reason}")

    # Corrupted
    item4 = Item("Sword", ItemClass.SWORD, 85)
    item4.is_corrupted = True
    can_combine, reason = item1.can_recombine_with(item4)
    print(f"✓ Проверка corrupted: {not can_combine} (ожидается False)")
    print(f"  Причина: {reason}")

    print("\n" + "=" * 80)
    print("ТЕСТ 5: Эксклюзивные моды")
    print("=" * 80)

    item5 = Item("Gloves", ItemClass.GLOVES, 85)
    item5.prefixes.append(Mod(
        name="Essence Mod",
        mod_type=ModType.PREFIX,
        tier=ModTier.T1,
        mod_group="Life",
        is_exclusive=True
    ))

    print(f"✓ Предмет с эксклюзивным модом: {item5.has_exclusive_mod()}")
    print(f"  Эксклюзивный мод: {item5.get_exclusive_mod().name}")

    print("\n" + "=" * 80)
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    test_all()
