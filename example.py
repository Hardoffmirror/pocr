#!/usr/bin/env python3
"""
Демонстрационный пример использования симулятора рекомбинаторов
"""

from models import Item, Mod, ModType, ModTier, ItemClass
from calculator import RecombinatorCalculator
from simulator import RecombinatorSimulator


def example_1_simple_recombination():
    """Пример 1: Простая рекомбинация двух предметов"""
    print("=" * 80)
    print("ПРИМЕР 1: Простая рекомбинация двух предметов")
    print("=" * 80)
    print()

    # Создаем первый предмет - меч с 2 префиксами
    item1 = Item(
        name="Rare Sword 1",
        item_class=ItemClass.SWORD,
        item_level=85
    )

    # Добавляем моды
    item1.prefixes.append(Mod(
        name="+100 to Maximum Life",
        mod_type=ModType.PREFIX,
        tier=ModTier.T1,
        mod_group="Life",
        current_value=100
    ))

    item1.prefixes.append(Mod(
        name="+50% Increased Physical Damage",
        mod_type=ModType.PREFIX,
        tier=ModTier.T2,
        mod_group="PhysicalDamage",
        current_value=50
    ))

    item1.suffixes.append(Mod(
        name="+45% to Critical Strike Chance",
        mod_type=ModType.SUFFIX,
        tier=ModTier.T1,
        mod_group="CriticalChance",
        current_value=45
    ))

    # Создаем второй предмет - меч с 1 префиксом и 2 суффиксами
    item2 = Item(
        name="Rare Sword 2",
        item_class=ItemClass.SWORD,
        item_level=85
    )

    item2.prefixes.append(Mod(
        name="+30% Increased Attack Speed",
        mod_type=ModType.PREFIX,
        tier=ModTier.T1,
        mod_group="AttackSpeed",
        current_value=30
    ))

    item2.suffixes.append(Mod(
        name="+40% to Critical Strike Multiplier",
        mod_type=ModType.SUFFIX,
        tier=ModTier.T2,
        mod_group="CriticalMultiplier",
        current_value=40
    ))

    item2.suffixes.append(Mod(
        name="+30% to Cold Resistance",
        mod_type=ModType.SUFFIX,
        tier=ModTier.T3,
        mod_group="ColdResistance",
        current_value=30
    ))

    # Выводим предметы
    print("Предмет 1:")
    print(item1)
    print("\n" + "-" * 80 + "\n")

    print("Предмет 2:")
    print(item2)
    print("\n" + "-" * 80 + "\n")

    # Проверяем совместимость
    can_combine, reason = item1.can_recombine_with(item2)
    print(f"Можно рекомбинировать? {can_combine}")
    if not can_combine:
        print(f"Причина: {reason}")
    print()

    # Рассчитываем вероятности
    calculator = RecombinatorCalculator()
    outcomes = calculator.analyze_all_outcomes(item1, item2)
    stats = calculator.get_statistics_summary(outcomes)

    print("СТАТИСТИКА:")
    print(f"Всего возможных исходов: {stats['total_outcomes']}")
    print(f"Средний шанс успеха: {stats['average_success_rate']:.2%}")
    print(f"Вероятность получить ≥2P и ≥2S: {stats['probability_2_2_or_better']:.2%}")
    print(f"Вероятность получить 3P и 3S: {stats['probability_3_3']:.2%}")
    print()

    # Показываем топ-5 наиболее вероятных исходов
    print("ТОП-5 НАИБОЛЕЕ ВЕРОЯТНЫХ ИСХОДОВ:")
    for i, outcome in enumerate(outcomes[:5], 1):
        print(f"\n#{i}. {outcome['prefix_count']}P + {outcome['suffix_count']}S")
        print(f"   Общая вероятность: {outcome['combined_probability']:.4%}")
        print(f"   Шанс выбора: {outcome['selection_probability']:.4%}")
        print(f"   Шанс успеха: {outcome['success_probability']:.2%}")

    print("\n")


def example_2_simulation():
    """Пример 2: Симуляция 1000 рекомбинаций"""
    print("=" * 80)
    print("ПРИМЕР 2: Симуляция 1000 рекомбинаций")
    print("=" * 80)
    print()

    # Создаем два простых предмета
    item1 = Item(
        name="Simple Ring 1",
        item_class=ItemClass.RING,
        item_level=80
    )

    item1.prefixes.append(Mod(
        name="+70 to Maximum Life",
        mod_type=ModType.PREFIX,
        tier=ModTier.T2,
        mod_group="Life"
    ))

    item1.suffixes.append(Mod(
        name="+40% to Fire Resistance",
        mod_type=ModType.SUFFIX,
        tier=ModTier.T2,
        mod_group="FireResistance"
    ))

    item2 = Item(
        name="Simple Ring 2",
        item_class=ItemClass.RING,
        item_level=80
    )

    item2.prefixes.append(Mod(
        name="+50 to Maximum Mana",
        mod_type=ModType.PREFIX,
        tier=ModTier.T3,
        mod_group="Mana"
    ))

    item2.suffixes.append(Mod(
        name="+35% to Lightning Resistance",
        mod_type=ModType.SUFFIX,
        tier=ModTier.T3,
        mod_group="LightningResistance"
    ))

    # Запускаем симуляцию
    simulator = RecombinatorSimulator()
    results = simulator.simulate_multiple_recombinations(item1, item2, 1000)

    print(f"Запущено симуляций: {results['total_simulations']}")
    print(f"Успехов: {results['successes']} ({results['success_rate']:.2%})")
    print(f"Провалов: {results['failures']}")
    print(f"Среднее кол-во префиксов: {results['average_prefixes']:.2f}")
    print(f"Среднее кол-во суффиксов: {results['average_suffixes']:.2f}")
    print()

    print("РАСПРЕДЕЛЕНИЕ РЕЗУЛЬТАТОВ:")
    for (p, s), count in sorted(results['results_distribution'].items()):
        percentage = (count / results['successes']) * 100 if results['successes'] > 0 else 0
        print(f"  {p}P x {s}S: {count} раз ({percentage:.1f}%)")

    print("\n")


def example_3_exclusive_mods():
    """Пример 3: Работа с эксклюзивными модами"""
    print("=" * 80)
    print("ПРИМЕР 3: Рекомбинация с эксклюзивным модом (essence)")
    print("=" * 80)
    print()

    # Предмет с essence модом
    item1 = Item(
        name="Essence Crafted Gloves",
        item_class=ItemClass.GLOVES,
        item_level=85
    )

    item1.prefixes.append(Mod(
        name="+120 to Maximum Life [ESSENCE]",
        mod_type=ModType.PREFIX,
        tier=ModTier.T1,
        mod_group="Life",
        is_exclusive=True,
        current_value=120
    ))

    item1.suffixes.append(Mod(
        name="+45% to Fire Resistance",
        mod_type=ModType.SUFFIX,
        tier=ModTier.T1,
        mod_group="FireResistance"
    ))

    # Обычный предмет
    item2 = Item(
        name="Normal Gloves",
        item_class=ItemClass.GLOVES,
        item_level=85
    )

    item2.prefixes.append(Mod(
        name="+50 to Strength",
        mod_type=ModType.PREFIX,
        tier=ModTier.T2,
        mod_group="Strength"
    ))

    item2.suffixes.append(Mod(
        name="+40% to Cold Resistance",
        mod_type=ModType.SUFFIX,
        tier=ModTier.T2,
        mod_group="ColdResistance"
    ))

    print("Предмет 1 (с эксклюзивным модом):")
    print(item1)
    print("\n" + "-" * 80 + "\n")

    print("Предмет 2 (обычный):")
    print(item2)
    print("\n" + "-" * 80 + "\n")

    # Рассчитываем вероятности
    calculator = RecombinatorCalculator()
    outcomes = calculator.analyze_all_outcomes(item1, item2)

    # Смотрим исходы с эксклюзивным модом
    exclusive_outcomes = [o for o in outcomes
                         if any(m.is_exclusive for m in o['prefixes'])]

    print(f"Исходов с сохранением эксклюзивного мода: {len(exclusive_outcomes)}")
    if exclusive_outcomes:
        most_likely = exclusive_outcomes[0]
        print(f"Наиболее вероятный исход: {most_likely['prefix_count']}P + {most_likely['suffix_count']}S")
        print(f"Вероятность: {most_likely['combined_probability']:.4%}")

    print("\n")


def example_4_mod_groups():
    """Пример 4: Моды из одной группы"""
    print("=" * 80)
    print("ПРИМЕР 4: Моды из одной группы (можно выбрать только один)")
    print("=" * 80)
    print()

    # Два предмета с модами из одной группы (Life)
    item1 = Item(
        name="Belt 1",
        item_class=ItemClass.BELT,
        item_level=85
    )

    item1.prefixes.append(Mod(
        name="+100 to Maximum Life",
        mod_type=ModType.PREFIX,
        tier=ModTier.T1,
        mod_group="Life",
        current_value=100
    ))

    item2 = Item(
        name="Belt 2",
        item_class=ItemClass.BELT,
        item_level=85
    )

    item2.prefixes.append(Mod(
        name="+80 to Maximum Life",
        mod_type=ModType.PREFIX,
        tier=ModTier.T2,
        mod_group="Life",
        current_value=80
    ))

    print("Оба предмета имеют моды из группы 'Life'")
    print()
    print("Предмет 1:")
    print(item1)
    print()
    print("Предмет 2:")
    print(item2)
    print()

    print("ВАЖНО: Из группы 'Life' может быть выбран только ОДИН мод!")
    print("Результат будет иметь либо T1 Life, либо T2 Life, либо вообще без Life.")
    print()

    # Симулируем
    simulator = RecombinatorSimulator()
    results = simulator.simulate_multiple_recombinations(item1, item2, 100)

    print(f"После 100 симуляций:")
    print(f"Успехов: {results['successes']}")
    print(f"Провалов: {results['failures']}")

    print("\n")


def main():
    """Запуск всех примеров"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "POE RECOMBINATOR SIMULATOR" + " " * 32 + "║")
    print("║" + " " * 25 + "DEMO EXAMPLES" + " " * 40 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    try:
        example_1_simple_recombination()
        input("Нажмите Enter для продолжения...")
        print("\n")

        example_2_simulation()
        input("Нажмите Enter для продолжения...")
        print("\n")

        example_3_exclusive_mods()
        input("Нажмите Enter для продолжения...")
        print("\n")

        example_4_mod_groups()
        print("\n")

        print("=" * 80)
        print("Все примеры выполнены успешно!")
        print("Запустите 'python main.py' для использования GUI версии")
        print("=" * 80)

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
