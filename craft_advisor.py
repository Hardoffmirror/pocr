"""
Советник по крафту - анализирует ситуацию и рекомендует оптимальную стратегию
"""
from typing import List, Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

from models import Item, Mod, ModType
from calculator import RecombinatorCalculator


class CraftStrategy(Enum):
    """Тип стратегии крафта"""
    BASIC = "Базовая рекомбинация"
    EXCLUSIVE = "С эксклюзивными модами"
    NNN = "С NNN модами"
    HYBRID = "Гибридная стратегия"
    IMPOSSIBLE = "Невозможно"


@dataclass
class CraftRecommendation:
    """Рекомендация по крафту"""
    strategy: CraftStrategy
    success_probability: float
    average_attempts: int
    estimated_cost: Dict[str, int]
    steps: List[str]
    warnings: List[str]
    tips: List[str]
    feasibility: str  # "Легко", "Средне", "Сложно", "Очень сложно", "Невозможно"


class CraftAdvisor:
    """Советник по оптимальной стратегии крафта"""

    def __init__(self):
        self.calculator = RecombinatorCalculator()

    def analyze_desired_outcome(
        self,
        desired_prefixes: List[Mod],
        desired_suffixes: List[Mod],
        available_mods_item1: List[Mod] = None,
        available_mods_item2: List[Mod] = None
    ) -> CraftRecommendation:
        """
        Анализ желаемого результата и рекомендация стратегии

        Args:
            desired_prefixes: Желаемые префиксы
            desired_suffixes: Желаемые суффиксы
            available_mods_item1: Доступные моды на предмете 1 (если есть)
            available_mods_item2: Доступные моды на предмете 2 (если есть)

        Returns:
            Рекомендация с оптимальной стратегией
        """
        total_desired = len(desired_prefixes) + len(desired_suffixes)

        # Проверка базовых ограничений
        if len(desired_prefixes) > 3 or len(desired_suffixes) > 3:
            return self._create_impossible_recommendation(
                "Невозможно получить более 3 префиксов или 3 суффиксов"
            )

        # Проверка на эксклюзивные моды
        exclusive_count = sum(1 for mod in desired_prefixes + desired_suffixes
                            if mod.is_exclusive)
        if exclusive_count > 1:
            return self._create_impossible_recommendation(
                "Невозможно иметь более одного эксклюзивного мода"
            )

        # Определение оптимальной стратегии
        if total_desired <= 3:
            return self._recommend_basic_strategy(desired_prefixes, desired_suffixes)
        elif 4 <= total_desired <= 5:
            if exclusive_count == 1:
                return self._recommend_exclusive_strategy(
                    desired_prefixes, desired_suffixes
                )
            else:
                return self._recommend_exclusive_strategy(
                    desired_prefixes, desired_suffixes,
                    add_exclusive=True
                )
        else:
            return self._recommend_hybrid_strategy(desired_prefixes, desired_suffixes)

    def _recommend_basic_strategy(
        self,
        prefixes: List[Mod],
        suffixes: List[Mod]
    ) -> CraftRecommendation:
        """Рекомендация базовой стратегии (до 3 модов одного типа)"""

        total = len(prefixes) + len(suffixes)

        # Расчет вероятности
        if len(prefixes) == 3 and len(suffixes) == 0:
            # 3 префикса
            base_prob = 0.31  # 4→3 из таблицы
            attempts = int(1 / base_prob)
        elif len(suffixes) == 3 and len(prefixes) == 0:
            # 3 суффикса
            base_prob = 0.31
            attempts = int(1 / base_prob)
        elif len(prefixes) == 2 and len(suffixes) == 0:
            base_prob = 0.33  # 2→2
            attempts = int(1 / base_prob)
        elif len(suffixes) == 2 and len(prefixes) == 0:
            base_prob = 0.33
            attempts = int(1 / base_prob)
        else:
            # Смешанный случай
            base_prob = 0.25
            attempts = int(1 / base_prob)

        steps = [
            "БАЗОВАЯ РЕКОМБИНАЦИЯ - Пошаговый план:",
            "",
            "Шаг 1: Подготовка баз",
            f"  • Купите ~{attempts * 6} баз нужного типа",
            "  • Используйте Regex на poe.re для поиска нужных модов",
            f"  • Накатайте Orb of Alteration для получения 1-модных баз",
            "",
            "Шаг 2: Создание 2-модных баз",
            "  • Объедините 1-модные базы попарно",
            f"  • Вероятность успеха: ~33%",
            f"  • Понадобится ~{attempts * 3} попыток для {attempts} баз",
            "",
            "Шаг 3: Создание финальной базы",
            f"  • Объедините 2-модные базы для получения {total}-модной",
            f"  • Вероятность успеха: ~{base_prob:.0%}",
            f"  • В среднем нужно {attempts} попыток",
            "",
            "💡 Совет: Не забудьте добавить любой мод на magic базы перед",
            "   рекомбинацией чтобы сэкономить Thaumaturgic Dust!"
        ]

        cost = {
            "Orb of Alteration": attempts * 6 * 50,  # ~50 альтов на базу
            "Базы": attempts * 6,
            "Thaumaturgic Dust": attempts * 3 * 100,  # примерная стоимость
            "Попытки рекомбинации": attempts * 3
        }

        warnings = []
        if total == 3:
            warnings.append("⚠️ Для 3 модов одного типа потребуется много попыток")

        tips = [
            "✓ Используйте одинаковые группы модов на разных базах",
            "✓ Сохраняйте 'неудачные' базы с 1-2 нужными модами",
            "✓ Проверяйте совместимость баз перед крафтом"
        ]

        feasibility = self._determine_feasibility(base_prob, attempts)

        return CraftRecommendation(
            strategy=CraftStrategy.BASIC,
            success_probability=base_prob,
            average_attempts=attempts,
            estimated_cost=cost,
            steps=steps,
            warnings=warnings,
            tips=tips,
            feasibility=feasibility
        )

    def _recommend_exclusive_strategy(
        self,
        prefixes: List[Mod],
        suffixes: List[Mod],
        add_exclusive: bool = False
    ) -> CraftRecommendation:
        """Рекомендация стратегии с эксклюзивными модами (4-5 модов)"""

        total = len(prefixes) + len(suffixes)

        # Для 4-5 модов вероятность выше с exclusive стратегией
        base_prob = 0.15 if total == 5 else 0.25
        attempts = int(1 / base_prob)

        has_exclusive = any(m.is_exclusive for m in prefixes + suffixes)

        steps = [
            "ПРОДВИНУТАЯ РЕКОМБИНАЦИЯ С ЭКСКЛЮЗИВНЫМИ МОДАМИ:",
            "",
            "Принцип: Если выбран exclusive мод, ВСЕ другие exclusive удаляются,",
            "но обычные моды остаются! Это повышает шанс получить все желаемые моды.",
            "",
            "Шаг 1: Подготовка первой базы",
            f"  • Создайте базу с {len(prefixes)} префиксами + {len(suffixes)} суффиксами",
            "  • Накатайте Alterations для нужных модов",
            "  • Используйте базовую рекомбинацию для объединения",
        ]

        if not has_exclusive:
            steps.extend([
                "",
                "Шаг 2: Добавление эксклюзивных модов на базу 1",
                "  • Добавьте крафты:",
                "    - Can have 3 Crafted Modifiers",
                "    - Chance to Block Attacks",
                "    - +# to maximum Fortification while Focused",
                "  • Добавьте Beast Aspect (любой)",
                "  • Итого: 4 эксклюзивных мода",
            ])
        else:
            steps.extend([
                "",
                "Шаг 2: Добавление доп. эксклюзивных модов",
                "  • У вас уже есть 1 exclusive мод (essence/fossil)",
                "  • Добавьте ещё 2-3 крафта для заполнения",
            ])

        steps.extend([
            "",
            "Шаг 3: Подготовка второй базы",
            f"  • Создайте базу с оставшимися желаемыми модами",
            "  • Убедитесь что все желаемые моды распределены между базами",
            "",
            "Шаг 4: Заполнение второй базы эксклюзивными модами",
            "  • Добавьте 3-4 эксклюзивных крафта",
            "  • Заполните все слоты (6 модов на каждой базе)",
            "",
            "Шаг 5: Рекомбинация!",
            f"  • При выборе exclusive мода - все желаемые моды переносятся",
            f"  • Вероятность успеха: ~{base_prob:.0%}",
            f"  • В среднем нужно {attempts} попыток",
            "",
            "💡 ВАЖНО: Если получили 4 мода - можно повторить процесс",
            "   для добавления 5-го мода используя ту же технику!"
        ])

        cost = {
            "Базы": attempts * 4,
            "Orb of Alteration": attempts * 4 * 100,
            "Crafted mods (Divine Orbs)": 10,  # на крафты
            "Beast Aspect": 2,
            "Thaumaturgic Dust": attempts * 500,
            "Попытки рекомбинации": attempts * 2
        }

        warnings = [
            "⚠️ Требуется заполнить базы крафтами - это стоит Divine Orbs",
            "⚠️ Если провалили - сохраните базу с хорошими модами для повтора",
        ]

        if total == 5:
            warnings.append("⚠️ Для 5 модов потребуется терпение и ресурсы")

        tips = [
            "✓ Распределите желаемые моды между базами равномерно",
            "✓ Используйте 'провальные' базы повторно",
            "✓ Убедитесь что у вас разные эксклюзивные моды",
            "✓ Для 5 модов делайте в 2 этапа: сначала 4, потом 5"
        ]

        feasibility = self._determine_feasibility(base_prob, attempts)

        return CraftRecommendation(
            strategy=CraftStrategy.EXCLUSIVE,
            success_probability=base_prob,
            average_attempts=attempts,
            estimated_cost=cost,
            steps=steps,
            warnings=warnings,
            tips=tips,
            feasibility=feasibility
        )

    def _recommend_hybrid_strategy(
        self,
        prefixes: List[Mod],
        suffixes: List[Mod]
    ) -> CraftRecommendation:
        """Гибридная стратегия для особых случаев"""

        total = len(prefixes) + len(suffixes)
        base_prob = 0.10
        attempts = int(1 / base_prob)

        steps = [
            "ГИБРИДНАЯ СТРАТЕГИЯ:",
            "",
            "Этот случай требует комбинации нескольких техник.",
            "",
            "Рекомендуется разбить на этапы:",
            f"1. Сначала получите 3-4 мода базовой рекомбинацией",
            f"2. Затем добавьте оставшиеся через exclusive стратегию",
            "",
            "Обратитесь к вкладке 'Гайд' для детального понимания."
        ]

        cost = {
            "Ресурсы": "Много",
            "Время": "Долго"
        }

        warnings = [
            "⚠️ Сложная стратегия требующая опыта",
            "⚠️ Рекомендуется изучить гайд подробно"
        ]

        tips = [
            "✓ Используйте симулятор для тестирования",
            "✓ Планируйте каждый этап отдельно"
        ]

        return CraftRecommendation(
            strategy=CraftStrategy.HYBRID,
            success_probability=base_prob,
            average_attempts=attempts,
            estimated_cost=cost,
            steps=steps,
            warnings=warnings,
            tips=tips,
            feasibility="Очень сложно"
        )

    def _create_impossible_recommendation(self, reason: str) -> CraftRecommendation:
        """Создание рекомендации для невозможного случая"""
        return CraftRecommendation(
            strategy=CraftStrategy.IMPOSSIBLE,
            success_probability=0.0,
            average_attempts=0,
            estimated_cost={},
            steps=[f"❌ НЕВОЗМОЖНО: {reason}"],
            warnings=[reason],
            tips=["Пересмотрите желаемые моды"],
            feasibility="Невозможно"
        )

    def _determine_feasibility(self, probability: float, attempts: int) -> str:
        """Определение сложности крафта"""
        if probability >= 0.30:
            return "Легко"
        elif probability >= 0.20:
            return "Средне"
        elif probability >= 0.10:
            return "Сложно"
        else:
            return "Очень сложно"

    def check_mod_compatibility(
        self,
        mod1: Mod,
        mod2: Mod
    ) -> Tuple[bool, str]:
        """
        Проверка совместимости двух модов

        Returns:
            (совместимы ли, причина если нет)
        """
        # Проверка групп
        if mod1.mod_group == mod2.mod_group:
            return False, f"Моды из одной группы '{mod1.mod_group}'"

        # Проверка типов
        if mod1.mod_type != mod2.mod_type:
            return True, ""  # Префикс + Суффикс = ОК

        # Оба одного типа - проверяем эксклюзивность
        if mod1.is_exclusive and mod2.is_exclusive:
            return False, "Два эксклюзивных мода"

        return True, ""

    def validate_desired_combination(
        self,
        desired_mods: List[Mod]
    ) -> Tuple[bool, List[str]]:
        """
        Валидация желаемой комбинации модов

        Returns:
            (валидна ли, список проблем)
        """
        issues = []

        # Подсчет типов
        prefixes = [m for m in desired_mods if m.mod_type == ModType.PREFIX]
        suffixes = [m for m in desired_mods if m.mod_type == ModType.SUFFIX]

        if len(prefixes) > 3:
            issues.append(f"Слишком много префиксов ({len(prefixes)}/3)")

        if len(suffixes) > 3:
            issues.append(f"Слишком много суффиксов ({len(suffixes)}/3)")

        # Проверка групп
        seen_groups = set()
        for mod in desired_mods:
            if mod.mod_group in seen_groups:
                issues.append(f"Дубликат группы '{mod.mod_group}'")
            seen_groups.add(mod.mod_group)

        # Проверка эксклюзивных
        exclusive_mods = [m for m in desired_mods if m.is_exclusive]
        if len(exclusive_mods) > 1:
            issues.append(f"Более одного эксклюзивного мода ({len(exclusive_mods)})")

        return len(issues) == 0, issues
