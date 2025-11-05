"""
Парсер предметов Path of Exile из текстового формата
"""
import re
from typing import Optional, List, Tuple
from models import Item, Mod, ModType, ModTier, ItemClass


class ItemParser:
    """Парсер для импорта предметов из текстового формата PoE"""

    # Маппинг классов предметов (русский -> английский)
    ITEM_CLASS_MAP = {
        'кольца': ItemClass.RING,
        'кольцо': ItemClass.RING,
        'амулеты': ItemClass.AMULET,
        'амулет': ItemClass.AMULET,
        'пояса': ItemClass.BELT,
        'пояс': ItemClass.BELT,
        'перчатки': ItemClass.GLOVES,
        'шлемы': ItemClass.HELMET,
        'шлем': ItemClass.HELMET,
        'нагрудные доспехи': ItemClass.BODY_ARMOUR,
        'доспехи': ItemClass.BODY_ARMOUR,
        'ботинки': ItemClass.BOOTS,
        'сапоги': ItemClass.BOOTS,
        'мечи': ItemClass.SWORD,
        'меч': ItemClass.SWORD,
        'топоры': ItemClass.AXE,
        'топор': ItemClass.AXE,
        'булавы': ItemClass.MACE,
        'булава': ItemClass.MACE,
        'луки': ItemClass.BOW,
        'лук': ItemClass.BOW,
        'посохи': ItemClass.STAFF,
        'посох': ItemClass.STAFF,
        'жезлы': ItemClass.WAND,
        'жезл': ItemClass.WAND,
        'кинжалы': ItemClass.DAGGER,
        'кинжал': ItemClass.DAGGER,
        'когти': ItemClass.CLAW,
        'коготь': ItemClass.CLAW,
        'скипетры': ItemClass.SCEPTRE,
        'скипетр': ItemClass.SCEPTRE,
    }

    # Распространенные префиксы (для определения типа мода)
    COMMON_PREFIXES = {
        'жизн': 'Life',
        'энергетического щита': 'EnergyShield',
        'энергетическ': 'EnergyShield',
        'брон': 'Armour',
        'уклонени': 'Evasion',
        'ман': 'Mana',
        'сил': 'Strength',
        'ловкост': 'Dexterity',
        'интеллект': 'Intelligence',
        'физического урона': 'PhysicalDamage',
        'скорости атаки': 'AttackSpeed',
        'скорости сотворения': 'CastSpeed',
    }

    COMMON_SUFFIXES = {
        'сопротивлению огн': 'FireResistance',
        'сопротивлению холод': 'ColdResistance',
        'сопротивлению молни': 'LightningResistance',
        'сопротивлению хаос': 'ChaosResistance',
        'сопротивлению всем стихиям': 'AllResistances',
        'критического удара': 'CriticalChance',
        'множителю критического': 'CriticalMultiplier',
        'редкости': 'Rarity',
        'количества': 'Quantity',
    }

    @staticmethod
    def parse_item_text(text: str) -> Optional[Item]:
        """
        Парсинг текста предмета из игры

        Args:
            text: Текст предмета (скопированный из игры)

        Returns:
            Объект Item или None если не удалось распарсить
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if not lines:
            return None

        # Инициализируем переменные
        item_class = None
        item_name = None
        item_level = 1
        rarity = "Rare"
        mods = []
        is_corrupted = False

        # Парсим построчно
        i = 0
        while i < len(lines):
            line = lines[i]

            # Класс предмета
            if 'класс предмета:' in line.lower():
                class_text = line.split(':')[1].strip().lower()
                item_class = ItemParser._parse_item_class(class_text)

            # Редкость
            elif 'редкость:' in line.lower():
                rarity_text = line.split(':')[1].strip().lower()
                if 'редкий' in rarity_text:
                    rarity = "Rare"
                elif 'магический' in rarity_text or 'волшебный' in rarity_text:
                    rarity = "Magic"

            # Название предмета (обычно вторая строка после редкости)
            elif item_name is None and item_class is None and rarity != "Normal":
                item_name = line

            # Уровень предмета
            elif 'уровень предмета:' in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    item_level = int(match.group(1))

            # Corrupted
            elif 'осквернен' in line.lower() or 'corrupted' in line.lower():
                is_corrupted = True

            # Моды (строки с +, %, или числами)
            elif not line.startswith('-') and not line.startswith('Примечание'):
                if any(c in line for c in ['+', '%', 'к ', 'на ', 'повышение', 'понижение']):
                    # Пропускаем implicit моды
                    if '(implicit)' not in line.lower() and 'неявн' not in line.lower():
                        mod = ItemParser._parse_mod_line(line)
                        if mod:
                            mods.append(mod)

            i += 1

        # Если не нашли класс или название, пробуем определить из базы
        if not item_class and item_name:
            item_class = ItemParser._guess_item_class(item_name)

        if not item_class:
            item_class = ItemClass.RING  # По умолчанию

        if not item_name:
            item_name = f"Imported {item_class.value}"

        # Создаем предмет
        item = Item(
            name=item_name,
            item_class=item_class,
            item_level=item_level,
            rarity=rarity,
            is_corrupted=is_corrupted
        )

        # Распределяем моды по префиксам и суффиксам
        for mod in mods:
            if mod.mod_type == ModType.PREFIX:
                if len(item.prefixes) < 3:
                    item.prefixes.append(mod)
            else:
                if len(item.suffixes) < 3:
                    item.suffixes.append(mod)

        return item

    @staticmethod
    def _parse_item_class(class_text: str) -> Optional[ItemClass]:
        """Определение класса предмета из текста"""
        class_text = class_text.lower().strip()

        for key, value in ItemParser.ITEM_CLASS_MAP.items():
            if key in class_text:
                return value

        return None

    @staticmethod
    def _guess_item_class(item_name: str) -> Optional[ItemClass]:
        """Попытка определить класс из названия базы"""
        name_lower = item_name.lower()

        # Кольца
        if 'кольцо' in name_lower or 'ring' in name_lower:
            return ItemClass.RING

        # Амулеты
        if 'амулет' in name_lower or 'amulet' in name_lower:
            return ItemClass.AMULET

        # Пояса
        if 'пояс' in name_lower or 'belt' in name_lower:
            return ItemClass.BELT

        return None

    @staticmethod
    def _parse_mod_line(line: str) -> Optional[Mod]:
        """Парсинг строки мода"""
        # Проверяем на fractured
        is_fractured = 'fractured' in line.lower() or 'расколот' in line.lower()

        # Удаляем маркеры
        clean_line = re.sub(r'\(fractured\)|\(расколот.*?\)', '', line, flags=re.IGNORECASE)
        clean_line = clean_line.strip()

        # Извлекаем числовое значение
        value_match = re.search(r'[+\-]?(\d+)', clean_line)
        current_value = int(value_match.group(1)) if value_match else None

        # Определяем тип мода (префикс или суффикс)
        mod_type = ItemParser._determine_mod_type(clean_line)

        # Определяем группу мода
        mod_group = ItemParser._determine_mod_group(clean_line)

        # Определяем тир (упрощенно, на основе значения)
        tier = ItemParser._estimate_tier(clean_line, current_value)

        mod = Mod(
            name=clean_line,
            mod_type=mod_type,
            tier=tier,
            mod_group=mod_group,
            is_fractured=is_fractured,
            current_value=current_value
        )

        return mod

    @staticmethod
    def _determine_mod_type(mod_text: str) -> ModType:
        """Определение типа мода (префикс или суффикс)"""
        mod_lower = mod_text.lower()

        # Префиксы обычно содержат:
        for keyword in ItemParser.COMMON_PREFIXES.keys():
            if keyword in mod_lower:
                return ModType.PREFIX

        # Суффиксы обычно содержат:
        for keyword in ItemParser.COMMON_SUFFIXES.keys():
            if keyword in mod_lower:
                return ModType.SUFFIX

        # По умолчанию считаем суффиксом
        return ModType.SUFFIX

    @staticmethod
    def _determine_mod_group(mod_text: str) -> str:
        """Определение группы мода"""
        mod_lower = mod_text.lower()

        # Проверяем префиксы
        for keyword, group in ItemParser.COMMON_PREFIXES.items():
            if keyword in mod_lower:
                return group

        # Проверяем суффиксы
        for keyword, group in ItemParser.COMMON_SUFFIXES.items():
            if keyword in mod_lower:
                return group

        # Генерируем группу из текста мода
        # Берем ключевые слова
        words = re.findall(r'[а-яА-Яa-zA-Z]+', mod_text)
        if len(words) >= 2:
            return ''.join(words[-2:])
        elif words:
            return words[-1]

        return "Unknown"

    @staticmethod
    def _estimate_tier(mod_text: str, value: Optional[int]) -> ModTier:
        """
        Оценка тира мода на основе значения
        Это упрощенная оценка, для точности нужна полная база модов
        """
        if value is None:
            return ModTier.T3

        mod_lower = mod_text.lower()

        # Жизнь
        if 'жизн' in mod_lower:
            if value >= 90:
                return ModTier.T1
            elif value >= 70:
                return ModTier.T2
            elif value >= 60:
                return ModTier.T3
            else:
                return ModTier.T4

        # Сопротивления
        elif 'сопротивлен' in mod_lower:
            if 'всем' in mod_lower:
                if value >= 15:
                    return ModTier.T1
                else:
                    return ModTier.T2
            else:
                if value >= 45:
                    return ModTier.T1
                elif value >= 40:
                    return ModTier.T2
                elif value >= 35:
                    return ModTier.T3
                else:
                    return ModTier.T4

        # Энергетический щит
        elif 'энергетическ' in mod_lower:
            if value >= 50:
                return ModTier.T1
            elif value >= 40:
                return ModTier.T2
            else:
                return ModTier.T3

        # По умолчанию
        if value >= 40:
            return ModTier.T1
        elif value >= 30:
            return ModTier.T2
        elif value >= 20:
            return ModTier.T3
        else:
            return ModTier.T4


def test_parser():
    """Тест парсера"""
    sample_text = """
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
    item = parser.parse_item_text(sample_text)

    if item:
        print("Успешно распарсено!")
        print(item)
        print(f"\nМодов: {item.total_mod_count}")
        print(f"Fractured: {item.has_fractured_mod()}")
    else:
        print("Не удалось распарсить")


if __name__ == "__main__":
    test_parser()
