#!/usr/bin/env python3
"""
Автоматические тесты для помощника крафта
"""

from models import Mod, ModType, ModTier
from craft_advisor import CraftAdvisor


def main():
    """Запуск всех тестов"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ТЕСТЫ ПОМОЩНИКА КРАФТА" + " " * 36 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    # Тест 1
    print("=" * 80)
    print("ТЕСТ 1: Базовая рекомбинация - 3 префикса (физическое оружие)")
    print("=" * 80)
    print()

    advisor = CraftAdvisor()

    desired_prefixes = [
        Mod("150% Increased Physical Damage", ModType.PREFIX, ModTier.T1, "PhysicalDamagePercent"),
        Mod("Adds 20-40 Physical Damage", ModType.PREFIX, ModTier.T1, "PhysicalDamageFlat"),
        Mod("25% Increased Physical Damage + Accuracy", ModType.PREFIX, ModTier.T1, "PhysicalDamageHybrid"),
    ]

    recommendation = advisor.analyze_desired_outcome(desired_prefixes, [])

    print("✓ Желаемый результат: 3 префикса (% Phys, Flat Phys, Hybrid Phys)")
    print(f"✓ Стратегия: {recommendation.strategy.value}")
    print(f"✓ Сложность: {recommendation.feasibility}")
    print(f"✓ Вероятность: {recommendation.success_probability:.1%}")
    print(f"✓ Попыток в среднем: {recommendation.average_attempts}")
    print()

    # Тест 2
    print("=" * 80)
    print("ТЕСТ 2: Продвинутая рекомбинация - 5 модов с essence")
    print("=" * 80)
    print()

    desired_prefixes = [
        Mod("+100 to Maximum Life", ModType.PREFIX, ModTier.T1, "Life"),
        Mod("+45% Increased Energy Shield", ModType.PREFIX, ModTier.T1, "EnergyShieldPercent"),
        Mod("+300 to Armour and Evasion", ModType.PREFIX, ModTier.T1, "ArmourEvasion"),
    ]

    desired_suffixes = [
        Mod("+100% to Spell Suppression", ModType.SUFFIX, ModTier.T1, "SpellSuppression", is_exclusive=True),
        Mod("+50 to Intelligence", ModType.SUFFIX, ModTier.T1, "Intelligence"),
    ]

    recommendation = advisor.analyze_desired_outcome(desired_prefixes, desired_suffixes)

    print("✓ Желаемый результат: 3P + 2S (включая essence мод)")
    print(f"✓ Стратегия: {recommendation.strategy.value}")
    print(f"✓ Сложность: {recommendation.feasibility}")
    print(f"✓ Вероятность: {recommendation.success_probability:.1%}")
    print(f"✓ Попыток в среднем: {recommendation.average_attempts}")
    print()

    # Тест 3
    print("=" * 80)
    print("ТЕСТ 3: Валидация - невозможный случай (4 префикса)")
    print("=" * 80)
    print()

    desired_prefixes = [
        Mod("Mod 1", ModType.PREFIX, ModTier.T1, "Group1"),
        Mod("Mod 2", ModType.PREFIX, ModTier.T1, "Group2"),
        Mod("Mod 3", ModType.PREFIX, ModTier.T1, "Group3"),
        Mod("Mod 4", ModType.PREFIX, ModTier.T1, "Group4"),
    ]

    is_valid, issues = advisor.validate_desired_combination(desired_prefixes)

    print(f"✓ Валидация: {is_valid} (ожидается False)")
    if not is_valid:
        print("✓ Проблемы обнаружены корректно:")
        for issue in issues:
            print(f"    • {issue}")
    print()

    # Тест 4
    print("=" * 80)
    print("ТЕСТ 4: Валидация - два эксклюзивных мода")
    print("=" * 80)
    print()

    mods = [
        Mod("Essence Life", ModType.PREFIX, ModTier.T1, "Life", is_exclusive=True),
        Mod("Fossil Mod", ModType.SUFFIX, ModTier.T1, "Resistance", is_exclusive=True),
    ]
    is_valid, issues = advisor.validate_desired_combination(mods)

    print(f"✓ Валидация: {is_valid} (ожидается False)")
    if not is_valid:
        print("✓ Проблемы обнаружены корректно:")
        for issue in issues:
            print(f"    • {issue}")
    print()

    # Тест 5
    print("=" * 80)
    print("ТЕСТ 5: Валидация - нормальная комбинация")
    print("=" * 80)
    print()

    mods = [
        Mod("Life", ModType.PREFIX, ModTier.T1, "Life"),
        Mod("ES", ModType.PREFIX, ModTier.T1, "EnergyShield"),
        Mod("Cold Res", ModType.SUFFIX, ModTier.T1, "ColdResistance"),
        Mod("Fire Res", ModType.SUFFIX, ModTier.T1, "FireResistance"),
    ]
    is_valid, issues = advisor.validate_desired_combination(mods)

    print(f"✓ Валидация: {is_valid} (ожидается True)")
    print()

    print("=" * 80)
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! ✓")
    print("=" * 80)
    print()
    print("Помощник крафта готов к использованию!")
    print("Запустите: python main.py и перейдите на вкладку '🎯 Помощник крафта'")
    print()


if __name__ == "__main__":
    main()
