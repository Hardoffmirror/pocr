#!/usr/bin/env python3
"""
Тесты для помощника крафта
"""

from models import Mod, ModType, ModTier
from craft_advisor import CraftAdvisor


def test_basic_3_prefix():
    """Тест базовой рекомбинации - 3 префикса"""
    print("=" * 80)
    print("ТЕСТ 1: Базовая рекомбинация - 3 префикса (физическое оружие)")
    print("=" * 80)
    print()

    advisor = CraftAdvisor()

    # Желаемые моды для физического оружия
    desired_prefixes = [
        Mod("150% Increased Physical Damage", ModType.PREFIX, ModTier.T1, "PhysicalDamagePercent"),
        Mod("Adds 20-40 Physical Damage", ModType.PREFIX, ModTier.T1, "PhysicalDamageFlat"),
        Mod("25% Increased Physical Damage + Accuracy", ModType.PREFIX, ModTier.T1, "PhysicalDamageHybrid"),
    ]

    # Анализ
    recommendation = advisor.analyze_desired_outcome(desired_prefixes, [])

    print("Желаемый результат: 3 префикса (% Phys, Flat Phys, Hybrid Phys)")
    print()
    print(f"Стратегия: {recommendation.strategy.value}")
    print(f"Сложность: {recommendation.feasibility}")
    print(f"Вероятность: {recommendation.success_probability:.1%}")
    print(f"Попыток в среднем: {recommendation.average_attempts}")
    print()
    print("Пошаговый план:")
    for step in recommendation.steps[:10]:  # Первые 10 строк
        print(step)
    print()


def test_exclusive_5_mods():
    """Тест с эксклюзивными модами - 5 модов"""
    print("=" * 80)
    print("ТЕСТ 2: Продвинутая рекомбинация - 5 модов с essence")
    print("=" * 80)
    print()

    advisor = CraftAdvisor()

    # Желаемые моды для доспеха
    desired_prefixes = [
        Mod("+100 to Maximum Life", ModType.PREFIX, ModTier.T1, "Life"),
        Mod("+45% Increased Energy Shield", ModType.PREFIX, ModTier.T1, "EnergyShieldPercent"),
        Mod("+300 to Armour and Evasion", ModType.PREFIX, ModTier.T1, "ArmourEvasion"),
    ]

    desired_suffixes = [
        Mod("+100% to Spell Suppression", ModType.SUFFIX, ModTier.T1, "SpellSuppression", is_exclusive=True),  # Essence mod
        Mod("+50 to Intelligence", ModType.SUFFIX, ModTier.T1, "Intelligence"),
    ]

    # Анализ
    recommendation = advisor.analyze_desired_outcome(desired_prefixes, desired_suffixes)

    print("Желаемый результат: 3P + 2S (включая essence мод)")
    print()
    print(f"Стратегия: {recommendation.strategy.value}")
    print(f"Сложность: {recommendation.feasibility}")
    print(f"Вероятность: {recommendation.success_probability:.1%}")
    print(f"Попыток в среднем: {recommendation.average_attempts}")
    print()
    print("Предупреждения:")
    for warning in recommendation.warnings:
        print(f"  {warning}")
    print()
    print("Советы:")
    for tip in recommendation.tips[:3]:
        print(f"  {tip}")
    print()


def test_impossible_case():
    """Тест невозможного случая"""
    print("=" * 80)
    print("ТЕСТ 3: Невозможный случай - 4 префикса")
    print("=" * 80)
    print()

    advisor = CraftAdvisor()

    # Пытаемся получить 4 префикса
    desired_prefixes = [
        Mod("Mod 1", ModType.PREFIX, ModTier.T1, "Group1"),
        Mod("Mod 2", ModType.PREFIX, ModTier.T1, "Group2"),
        Mod("Mod 3", ModType.PREFIX, ModTier.T1, "Group3"),
        Mod("Mod 4", ModType.PREFIX, ModTier.T1, "Group4"),
    ]

    # Валидация
    is_valid, issues = advisor.validate_desired_combination(desired_prefixes)

    print(f"Валидно: {is_valid}")
    if not is_valid:
        print("Проблемы:")
        for issue in issues:
            print(f"  • {issue}")
    print()


def test_validation():
    """Тест валидации комбинаций"""
    print("=" * 80)
    print("ТЕСТ 4: Валидация различных комбинаций")
    print("=" * 80)
    print()

    advisor = CraftAdvisor()

    # Тест 1: Два мода одной группы
    print("Проверка: Два мода из одной группы")
    mods = [
        Mod("Life 1", ModType.PREFIX, ModTier.T1, "Life"),
        Mod("Life 2", ModType.PREFIX, ModTier.T2, "Life"),
    ]
    is_valid, issues = advisor.validate_desired_combination(mods)
    print(f"  Валидно: {is_valid}")
    if not is_valid:
        for issue in issues:
            print(f"    • {issue}")
    print()

    # Тест 2: Два эксклюзивных мода
    print("Проверка: Два эксклюзивных мода")
    mods = [
        Mod("Essence Life", ModType.PREFIX, ModTier.T1, "Life", is_exclusive=True),
        Mod("Fossil Mod", ModType.SUFFIX, ModTier.T1, "Resistance", is_exclusive=True),
    ]
    is_valid, issues = advisor.validate_desired_combination(mods)
    print(f"  Валидно: {is_valid}")
    if not is_valid:
        for issue in issues:
            print(f"    • {issue}")
    print()

    # Тест 3: Нормальная комбинация
    print("Проверка: Нормальная комбинация 2P + 2S")
    mods = [
        Mod("Life", ModType.PREFIX, ModTier.T1, "Life"),
        Mod("ES", ModType.PREFIX, ModTier.T1, "EnergyShield"),
        Mod("Cold Res", ModType.SUFFIX, ModTier.T1, "ColdResistance"),
        Mod("Fire Res", ModType.SUFFIX, ModTier.T1, "FireResistance"),
    ]
    is_valid, issues = advisor.validate_desired_combination(mods)
    print(f"  Валидно: {is_valid}")
    print()


def main():
    """Запуск всех тестов"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ТЕСТЫ ПОМОЩНИКА КРАФТА" + " " * 36 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    test_basic_3_prefix()
    input("Нажмите Enter для продолжения...")
    print("\n")

    test_exclusive_5_mods()
    input("Нажмите Enter для продолжения...")
    print("\n")

    test_impossible_case()
    input("Нажмите Enter для продолжения...")
    print("\n")

    test_validation()

    print("=" * 80)
    print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 80)
    print()
    print("Помощник крафта готов к использованию!")
    print("Запустите: python main.py")
    print("Перейдите на вкладку '🎯 Помощник крафта'")
    print()


if __name__ == "__main__":
    main()
