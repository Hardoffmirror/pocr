"""
Модели данных для симулятора рекомбинаторов Path of Exile
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class ModType(Enum):
    """Тип модификатора"""
    PREFIX = "Prefix"
    SUFFIX = "Suffix"


class ModTier(Enum):
    """Тир модификатора (влияет на вероятность успеха)"""
    T1 = 1
    T2 = 2
    T3 = 3
    T4 = 4
    T5 = 5
    T6 = 6


class ItemClass(Enum):
    """Класс предмета"""
    WEAPON = "Weapon"
    ARMOUR = "Armour"
    JEWELLERY = "Jewellery"
    HELMET = "Helmet"
    BODY_ARMOUR = "Body Armour"
    GLOVES = "Gloves"
    BOOTS = "Boots"
    BELT = "Belt"
    AMULET = "Amulet"
    RING = "Ring"
    SWORD = "Sword"
    AXE = "Axe"
    MACE = "Mace"
    BOW = "Bow"
    STAFF = "Staff"
    WAND = "Wand"
    DAGGER = "Dagger"
    CLAW = "Claw"
    SCEPTRE = "Sceptre"


@dataclass
class Mod:
    """Модификатор предмета"""
    name: str
    mod_type: ModType
    tier: ModTier
    mod_group: str  # Группа модификаторов (например, "Strength", "Life")
    is_exclusive: bool = False  # Эксклюзивный мод (например, essence mod)
    is_fractured: bool = False  # Фрактурированный мод
    is_influenced: bool = False  # Influenced мод
    influence_type: Optional[str] = None  # Тип influence (Shaper, Elder, etc.)
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    current_value: Optional[int] = None

    def __str__(self):
        value_str = ""
        if self.current_value is not None:
            value_str = f" ({self.current_value})"
        exclusive_str = " [EXCLUSIVE]" if self.is_exclusive else ""
        fractured_str = " [FRACTURED]" if self.is_fractured else ""
        influenced_str = f" [{self.influence_type}]" if self.is_influenced else ""
        return f"{self.name}{value_str} ({self.tier.name}){exclusive_str}{fractured_str}{influenced_str}"


@dataclass
class Item:
    """Предмет для рекомбинации"""
    name: str
    item_class: ItemClass
    item_level: int
    rarity: str = "Rare"  # Magic или Rare
    prefixes: List[Mod] = field(default_factory=list)
    suffixes: List[Mod] = field(default_factory=list)
    is_corrupted: bool = False
    is_mirrored: bool = False

    def __post_init__(self):
        if not self.prefixes:
            self.prefixes = []
        if not self.suffixes:
            self.suffixes = []

    @property
    def all_mods(self) -> List[Mod]:
        """Все модификаторы предмета"""
        return self.prefixes + self.suffixes

    @property
    def prefix_count(self) -> int:
        """Количество префиксов"""
        return len(self.prefixes)

    @property
    def suffix_count(self) -> int:
        """Количество суффиксов"""
        return len(self.suffixes)

    @property
    def total_mod_count(self) -> int:
        """Общее количество модов"""
        return self.prefix_count + self.suffix_count

    def has_exclusive_mod(self) -> bool:
        """Проверка наличия эксклюзивного мода"""
        return any(mod.is_exclusive for mod in self.all_mods)

    def get_exclusive_mod(self) -> Optional[Mod]:
        """Получить эксклюзивный мод если есть"""
        for mod in self.all_mods:
            if mod.is_exclusive:
                return mod
        return None

    def has_fractured_mod(self) -> bool:
        """Проверка наличия фрактурированного мода"""
        return any(mod.is_fractured for mod in self.all_mods)

    def can_recombine_with(self, other: 'Item') -> tuple[bool, str]:
        """
        Проверка возможности рекомбинации с другим предметом
        Возвращает (можно ли рекомбинировать, причина если нельзя)
        """
        if self.item_class != other.item_class:
            return False, "Предметы разных классов"

        if self.is_corrupted or other.is_corrupted:
            return False, "Один из предметов corrupted"

        if self.is_mirrored or other.is_mirrored:
            return False, "Один из предметов mirrored"

        # Проверка на два разных эксклюзивных мода
        self_exclusive = self.get_exclusive_mod()
        other_exclusive = other.get_exclusive_mod()

        if self_exclusive and other_exclusive:
            if self_exclusive.mod_group != other_exclusive.mod_group:
                return False, "Два разных эксклюзивных мода"

        return True, ""

    def __str__(self):
        lines = [
            f"{self.name} (iLvl {self.item_level})",
            f"Class: {self.item_class.value}",
            f"Rarity: {self.rarity}",
            "",
            "Prefixes:"
        ]

        if self.prefixes:
            for mod in self.prefixes:
                lines.append(f"  {mod}")
        else:
            lines.append("  (none)")

        lines.append("")
        lines.append("Suffixes:")

        if self.suffixes:
            for mod in self.suffixes:
                lines.append(f"  {mod}")
        else:
            lines.append("  (none)")

        return "\n".join(lines)


@dataclass
class RecombinationResult:
    """Результат рекомбинации"""
    success: bool
    result_item: Optional[Item] = None
    selected_mods: List[Mod] = field(default_factory=list)
    probability: float = 0.0
    message: str = ""

    def __str__(self):
        if self.success:
            return f"SUCCESS (prob: {self.probability:.2%})\n{self.result_item}"
        else:
            return f"FAILED (prob: {1-self.probability:.2%})\n{self.message}"
