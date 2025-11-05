"""
Симулятор рекомбинации для Path of Exile
"""
import random
from typing import List, Dict, Tuple, Optional
from models import Item, Mod, RecombinationResult, ModType
from calculator import RecombinatorCalculator
from copy import deepcopy


class RecombinatorSimulator:
    """Симулятор процесса рекомбинации"""

    def __init__(self):
        self.calculator = RecombinatorCalculator()
        self.simulation_history: List[RecombinationResult] = []

    def simulate_single_recombination(
        self,
        item1: Item,
        item2: Item,
        desired_prefixes: Optional[List[Mod]] = None,
        desired_suffixes: Optional[List[Mod]] = None,
        random_seed: Optional[int] = None
    ) -> RecombinationResult:
        """
        Симуляция одной рекомбинации

        Args:
            item1: Первый предмет
            item2: Второй предмет
            desired_prefixes: Желаемые префиксы (если None, выбираются случайно)
            desired_suffixes: Желаемые суффиксы (если None, выбираются случайно)
            random_seed: Seed для воспроизводимости результатов

        Returns:
            RecombinationResult с информацией о результате
        """
        if random_seed is not None:
            random.seed(random_seed)

        # Проверка совместимости
        can_combine, reason = item1.can_recombine_with(item2)
        if not can_combine:
            return RecombinationResult(
                success=False,
                message=f"Невозможно рекомбинировать: {reason}",
                probability=0.0
            )

        # Если желаемые моды не указаны, выбираем случайно
        if desired_prefixes is None or desired_suffixes is None:
            selected_prefixes, selected_suffixes = self._select_random_mods(item1, item2)
        else:
            selected_prefixes = desired_prefixes
            selected_suffixes = desired_suffixes

        # Расчет вероятностей
        sel_prob, succ_prob, comb_prob = self.calculator.calculate_combined_probability(
            item1, item2, selected_prefixes, selected_suffixes
        )

        # Определяем успех на основе вероятности
        roll = random.random()
        success = roll <= succ_prob

        if success:
            # Создаем результирующий предмет
            result_item = self._create_result_item(
                item1, item2, selected_prefixes, selected_suffixes
            )

            result = RecombinationResult(
                success=True,
                result_item=result_item,
                selected_mods=selected_prefixes + selected_suffixes,
                probability=comb_prob,
                message="Рекомбинация успешна!"
            )
        else:
            result = RecombinationResult(
                success=False,
                probability=comb_prob,
                message=f"Рекомбинация провалилась! (roll: {roll:.3f} > {succ_prob:.3f})"
            )

        self.simulation_history.append(result)
        return result

    def simulate_multiple_recombinations(
        self,
        item1: Item,
        item2: Item,
        num_simulations: int,
        desired_prefixes: Optional[List[Mod]] = None,
        desired_suffixes: Optional[List[Mod]] = None,
        target_outcome: Optional[Dict] = None
    ) -> Dict:
        """
        Симуляция множественных рекомбинаций для сбора статистики

        Args:
            item1: Первый предмет
            item2: Второй предмет
            num_simulations: Количество симуляций
            desired_prefixes: Желаемые префиксы
            desired_suffixes: Желаемые суффиксы
            target_outcome: Целевой результат для отслеживания

        Returns:
            Словарь со статистикой симуляций
        """
        successes = 0
        failures = 0
        target_hits = 0
        results_distribution: Dict[Tuple[int, int], int] = {}

        for i in range(num_simulations):
            result = self.simulate_single_recombination(
                deepcopy(item1),
                deepcopy(item2),
                desired_prefixes,
                desired_suffixes,
                random_seed=None  # Разные результаты для каждой симуляции
            )

            if result.success:
                successes += 1

                # Подсчитываем распределение результатов
                prefix_count = len([m for m in result.selected_mods if m.mod_type == ModType.PREFIX])
                suffix_count = len([m for m in result.selected_mods if m.mod_type == ModType.SUFFIX])
                key = (prefix_count, suffix_count)
                results_distribution[key] = results_distribution.get(key, 0) + 1

                # Проверяем, достигли ли целевого результата
                if target_outcome:
                    if self._matches_target(result, target_outcome):
                        target_hits += 1
            else:
                failures += 1

        success_rate = successes / num_simulations if num_simulations > 0 else 0
        target_rate = target_hits / num_simulations if num_simulations > 0 else 0

        return {
            'total_simulations': num_simulations,
            'successes': successes,
            'failures': failures,
            'success_rate': success_rate,
            'target_hits': target_hits,
            'target_hit_rate': target_rate,
            'results_distribution': results_distribution,
            'average_prefixes': self._calculate_average_prefixes(results_distribution, successes),
            'average_suffixes': self._calculate_average_suffixes(results_distribution, successes)
        }

    def _select_random_mods(
        self,
        item1: Item,
        item2: Item
    ) -> Tuple[List[Mod], List[Mod]]:
        """
        Случайный выбор модов для рекомбинации
        Учитывает ограничения: макс 3 префикса, макс 3 суффикса,
        только один мод из каждой группы
        """
        # Собираем все доступные моды
        all_prefixes = item1.prefixes + item2.prefixes
        all_suffixes = item1.suffixes + item2.suffixes

        # Фильтруем по группам
        unique_prefixes = self._filter_mods_by_groups(all_prefixes)
        unique_suffixes = self._filter_mods_by_groups(all_suffixes)

        # Случайно выбираем количество модов (0-3)
        num_prefixes = random.randint(0, min(3, len(unique_prefixes)))
        num_suffixes = random.randint(0, min(3, len(unique_suffixes)))

        # Выбираем случайные моды
        selected_prefixes = random.sample(unique_prefixes, num_prefixes) if num_prefixes > 0 else []
        selected_suffixes = random.sample(unique_suffixes, num_suffixes) if num_suffixes > 0 else []

        return selected_prefixes, selected_suffixes

    def _filter_mods_by_groups(self, mods: List[Mod]) -> List[Mod]:
        """
        Фильтрация модов по группам - если несколько модов одной группы,
        оставляем только один (случайный)
        """
        mod_groups: Dict[str, List[Mod]] = {}

        for mod in mods:
            if mod.mod_group not in mod_groups:
                mod_groups[mod.mod_group] = []
            mod_groups[mod.mod_group].append(mod)

        result = []
        for group_mods in mod_groups.values():
            # Если в группе несколько модов, выбираем случайный
            result.append(random.choice(group_mods))

        return result

    def _create_result_item(
        self,
        item1: Item,
        item2: Item,
        selected_prefixes: List[Mod],
        selected_suffixes: List[Mod]
    ) -> Item:
        """
        Создание результирующего предмета после успешной рекомбинации
        """
        # Выбираем базу (50% шанс для каждого предмета)
        base_item = random.choice([item1, item2])

        # Определяем item level результата (максимальный из двух)
        result_ilvl = max(item1.item_level, item2.item_level)

        # Создаем новый предмет
        result_item = Item(
            name=f"Recombined {base_item.item_class.value}",
            item_class=base_item.item_class,
            item_level=result_ilvl,
            rarity="Rare" if len(selected_prefixes) + len(selected_suffixes) > 1 else "Magic",
            prefixes=deepcopy(selected_prefixes),
            suffixes=deepcopy(selected_suffixes)
        )

        return result_item

    def _matches_target(self, result: RecombinationResult, target: Dict) -> bool:
        """
        Проверка соответствия результата целевому исходу
        """
        if not result.success or not result.result_item:
            return False

        target_prefixes = target.get('prefixes', [])
        target_suffixes = target.get('suffixes', [])

        # Проверяем наличие всех целевых префиксов
        for target_mod in target_prefixes:
            found = False
            for mod in result.result_item.prefixes:
                if mod.mod_group == target_mod.mod_group:
                    found = True
                    break
            if not found:
                return False

        # Проверяем наличие всех целевых суффиксов
        for target_mod in target_suffixes:
            found = False
            for mod in result.result_item.suffixes:
                if mod.mod_group == target_mod.mod_group:
                    found = True
                    break
            if not found:
                return False

        return True

    def _calculate_average_prefixes(
        self,
        distribution: Dict[Tuple[int, int], int],
        total_successes: int
    ) -> float:
        """Расчет среднего количества префиксов в успешных попытках"""
        if total_successes == 0:
            return 0.0

        total = sum(prefix_count * count
                   for (prefix_count, _), count in distribution.items())
        return total / total_successes

    def _calculate_average_suffixes(
        self,
        distribution: Dict[Tuple[int, int], int],
        total_successes: int
    ) -> float:
        """Расчет среднего количества суффиксов в успешных попытках"""
        if total_successes == 0:
            return 0.0

        total = sum(suffix_count * count
                   for (_, suffix_count), count in distribution.items())
        return total / total_successes

    def get_simulation_statistics(self) -> Dict:
        """Получить статистику всех симуляций"""
        if not self.simulation_history:
            return {'message': 'Нет данных о симуляциях'}

        total = len(self.simulation_history)
        successes = sum(1 for r in self.simulation_history if r.success)
        failures = total - successes

        return {
            'total_simulations': total,
            'successes': successes,
            'failures': failures,
            'success_rate': successes / total if total > 0 else 0
        }

    def clear_history(self):
        """Очистить историю симуляций"""
        self.simulation_history.clear()
