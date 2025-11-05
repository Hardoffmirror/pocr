"""
Калькулятор вероятностей для рекомбинаторов Path of Exile
"""
import math
from typing import List, Dict, Tuple
from models import Item, Mod, ModType
from itertools import combinations


class RecombinatorCalculator:
    """Калькулятор вероятностей рекомбинации"""

    # Базовые коэффициенты для расчета вероятности успеха
    # Эти значения основаны на community testing
    BASE_SUCCESS_RATE = 0.35  # 35% базовый шанс успеха
    MOD_COUNT_PENALTY = 0.05   # Штраф за каждый дополнительный мод
    TIER_PENALTY = 0.02        # Штраф за каждый тир (T1 = больше штраф)

    @staticmethod
    def calculate_mod_selection_probability(
        available_mods: List[Mod],
        desired_mods: List[Mod]
    ) -> float:
        """
        Расчет вероятности выбора конкретного набора модов

        Формула: последовательный выбор модов с уменьшением пула
        P = (n1/total) * (n2/(total-1)) * ... * (nk/(total-k+1))
        где n1, n2, ... nk - желаемые моды
        """
        if not desired_mods:
            return 1.0

        # Проверяем, что все желаемые моды есть в доступных
        for mod in desired_mods:
            if mod not in available_mods:
                return 0.0

        probability = 1.0
        remaining_pool = available_mods.copy()

        for desired_mod in desired_mods:
            if not remaining_pool:
                return 0.0

            pool_size = len(remaining_pool)
            probability *= (1.0 / pool_size)
            remaining_pool.remove(desired_mod)

        return probability

    @staticmethod
    def calculate_prefix_suffix_selection_probability(
        item1: Item,
        item2: Item,
        desired_prefixes: List[Mod],
        desired_suffixes: List[Mod]
    ) -> float:
        """
        Расчет вероятности выбора конкретных префиксов и суффиксов
        с учетом ограничений (макс 3 префикса, макс 3 суффикса)
        """
        if len(desired_prefixes) > 3 or len(desired_suffixes) > 3:
            return 0.0

        # Собираем все доступные префиксы и суффиксы
        all_prefixes = item1.prefixes + item2.prefixes
        all_suffixes = item1.suffixes + item2.suffixes

        # Убираем дубликаты по mod_group (можно выбрать только один мод из группы)
        unique_prefixes = RecombinatorCalculator._filter_by_mod_groups(all_prefixes)
        unique_suffixes = RecombinatorCalculator._filter_by_mod_groups(all_suffixes)

        # Расчет вероятности для префиксов
        prefix_prob = RecombinatorCalculator.calculate_mod_selection_probability(
            unique_prefixes, desired_prefixes
        )

        # Расчет вероятности для суффиксов
        suffix_prob = RecombinatorCalculator.calculate_mod_selection_probability(
            unique_suffixes, desired_suffixes
        )

        return prefix_prob * suffix_prob

    @staticmethod
    def _filter_by_mod_groups(mods: List[Mod]) -> List[Mod]:
        """
        Фильтрация модов по группам - если есть несколько модов одной группы,
        считаем их как единый выбор
        """
        mod_groups: Dict[str, List[Mod]] = {}

        for mod in mods:
            if mod.mod_group not in mod_groups:
                mod_groups[mod.mod_group] = []
            mod_groups[mod.mod_group].append(mod)

        # Возвращаем по одному моду из каждой группы
        # (в реальности можно выбрать любой из группы)
        result = []
        for group_mods in mod_groups.values():
            result.extend(group_mods)  # Включаем все варианты для расчета

        return result

    @staticmethod
    def calculate_success_rate(
        selected_mods: List[Mod],
        total_available_mods: int
    ) -> float:
        """
        Расчет вероятности успешной рекомбинации

        Формула основана на:
        - Количестве выбранных модов
        - Тире выбранных модов (T1 моды труднее)
        - Наличии эксклюзивных модов
        """
        base_rate = RecombinatorCalculator.BASE_SUCCESS_RATE

        # Штраф за количество модов
        mod_count_penalty = len(selected_mods) * RecombinatorCalculator.MOD_COUNT_PENALTY

        # Штраф за тиры модов (T1 = 1, сильнее штраф)
        tier_penalty = 0
        for mod in selected_mods:
            tier_value = mod.tier.value
            # T1 = 1, T2 = 2, etc. Чем меньше значение, тем выше тир, больше штраф
            tier_penalty += (7 - tier_value) * RecombinatorCalculator.TIER_PENALTY

        # Бонус за меньшее количество модов в пуле
        pool_bonus = 0.05 * (6 - total_available_mods) if total_available_mods < 6 else 0

        # Итоговый расчет
        final_rate = base_rate - mod_count_penalty - tier_penalty + pool_bonus

        # Ограничиваем диапазон 1% - 95%
        return max(0.01, min(0.95, final_rate))

    @staticmethod
    def calculate_combined_probability(
        item1: Item,
        item2: Item,
        desired_prefixes: List[Mod],
        desired_suffixes: List[Mod]
    ) -> Tuple[float, float, float]:
        """
        Расчет полной вероятности получения желаемого результата

        Возвращает:
        - Вероятность выбора нужных модов
        - Вероятность успеха крафта
        - Общая вероятность (произведение двух выше)
        """
        # Проверяем совместимость
        can_combine, reason = item1.can_recombine_with(item2)
        if not can_combine:
            return 0.0, 0.0, 0.0

        # Вероятность выбора модов
        selection_prob = RecombinatorCalculator.calculate_prefix_suffix_selection_probability(
            item1, item2, desired_prefixes, desired_suffixes
        )

        # Все выбранные моды
        all_selected_mods = desired_prefixes + desired_suffixes

        # Все доступные моды
        total_available = len(item1.all_mods) + len(item2.all_mods)

        # Вероятность успеха
        success_prob = RecombinatorCalculator.calculate_success_rate(
            all_selected_mods, total_available
        )

        # Общая вероятность
        combined_prob = selection_prob * success_prob

        return selection_prob, success_prob, combined_prob

    @staticmethod
    def analyze_all_outcomes(
        item1: Item,
        item2: Item,
        max_prefixes: int = 3,
        max_suffixes: int = 3
    ) -> List[Dict]:
        """
        Анализ всех возможных исходов рекомбинации

        Возвращает список словарей с информацией о каждом возможном исходе:
        - Выбранные префиксы
        - Выбранные суффиксы
        - Вероятность выбора
        - Вероятность успеха
        - Общая вероятность
        """
        results = []

        # Собираем все уникальные префиксы и суффиксы
        all_prefixes = RecombinatorCalculator._get_unique_mods_by_group(
            item1.prefixes + item2.prefixes
        )
        all_suffixes = RecombinatorCalculator._get_unique_mods_by_group(
            item1.suffixes + item2.suffixes
        )

        # Генерируем все возможные комбинации префиксов (0-3)
        for prefix_count in range(0, min(max_prefixes + 1, len(all_prefixes) + 1)):
            for prefix_combo in combinations(all_prefixes, prefix_count):
                # Генерируем все возможные комбинации суффиксов (0-3)
                for suffix_count in range(0, min(max_suffixes + 1, len(all_suffixes) + 1)):
                    for suffix_combo in combinations(all_suffixes, suffix_count):
                        prefix_list = list(prefix_combo)
                        suffix_list = list(suffix_combo)

                        sel_prob, succ_prob, comb_prob = (
                            RecombinatorCalculator.calculate_combined_probability(
                                item1, item2, prefix_list, suffix_list
                            )
                        )

                        results.append({
                            'prefixes': prefix_list,
                            'suffixes': suffix_list,
                            'prefix_count': len(prefix_list),
                            'suffix_count': len(suffix_list),
                            'selection_probability': sel_prob,
                            'success_probability': succ_prob,
                            'combined_probability': comb_prob
                        })

        # Сортируем по убыванию общей вероятности
        results.sort(key=lambda x: x['combined_probability'], reverse=True)

        return results

    @staticmethod
    def _get_unique_mods_by_group(mods: List[Mod]) -> List[Mod]:
        """
        Получить уникальные моды по группам
        (из каждой группы берем только один самый высокий тир)
        """
        mod_groups: Dict[str, Mod] = {}

        for mod in mods:
            if mod.mod_group not in mod_groups:
                mod_groups[mod.mod_group] = mod
            else:
                # Если в группе уже есть мод, берем с лучшим тиром
                existing = mod_groups[mod.mod_group]
                if mod.tier.value < existing.tier.value:  # Меньше = лучше (T1 < T2)
                    mod_groups[mod.mod_group] = mod

        return list(mod_groups.values())

    @staticmethod
    def get_statistics_summary(outcomes: List[Dict]) -> Dict:
        """
        Получить статистическую сводку по всем исходам
        """
        if not outcomes:
            return {}

        total_probability = sum(o['combined_probability'] for o in outcomes)
        average_success = sum(o['success_probability'] for o in outcomes) / len(outcomes)

        # Вероятность получить хотя бы 2 префикса и 2 суффикса
        good_outcomes = [o for o in outcomes
                        if o['prefix_count'] >= 2 and o['suffix_count'] >= 2]
        prob_good = sum(o['combined_probability'] for o in good_outcomes)

        # Вероятность получить 3 префикса и 3 суффикса
        perfect_outcomes = [o for o in outcomes
                           if o['prefix_count'] == 3 and o['suffix_count'] == 3]
        prob_perfect = sum(o['combined_probability'] for o in perfect_outcomes)

        return {
            'total_outcomes': len(outcomes),
            'total_probability': total_probability,
            'average_success_rate': average_success,
            'probability_2_2_or_better': prob_good,
            'probability_3_3': prob_perfect,
            'most_likely_outcome': outcomes[0] if outcomes else None
        }
