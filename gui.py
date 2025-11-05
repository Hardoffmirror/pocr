"""
GUI для симулятора рекомбинаторов Path of Exile
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import List, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from models import Item, Mod, ModType, ModTier, ItemClass
from simulator import RecombinatorSimulator
from calculator import RecombinatorCalculator
from item_parser import ItemParser
from craft_advisor import CraftAdvisor, CraftStrategy


class RecombinatorGUI:
    """Главное окно приложения"""

    def __init__(self, root):
        self.root = root
        self.root.title("PoE Recombinator Simulator")
        self.root.geometry("1400x900")

        # Инициализация симулятора и калькулятора
        self.simulator = RecombinatorSimulator()
        self.calculator = RecombinatorCalculator()
        self.advisor = CraftAdvisor()

        # Хранилище данных
        self.item1: Optional[Item] = None
        self.item2: Optional[Item] = None
        self.current_mods_item1: List[Mod] = []
        self.current_mods_item2: List[Mod] = []

        # Настройка стилей
        self._setup_styles()

        # Создание интерфейса
        self._create_menu()
        self._create_widgets()

    def _setup_styles(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        style.theme_use('clam')

        # Цвета в стиле PoE
        bg_color = '#1a1410'
        fg_color = '#d4af37'
        button_color = '#4a3f35'

        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground=fg_color)
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground=fg_color)
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Success.TLabel', foreground='#00ff00')
        style.configure('Fail.TLabel', foreground='#ff0000')

    def _create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Очистить всё", command=self._clear_all)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню Help
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="Инструкция", command=self._show_instructions)
        help_menu.add_command(label="О программе", command=self._show_about)

    def _create_widgets(self):
        """Создание виджетов интерфейса"""
        # Создаем notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Вкладка 1: Настройка предметов
        self.tab_setup = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_setup, text="Настройка предметов")
        self._create_setup_tab()

        # Вкладка 2: Калькулятор вероятностей
        self.tab_calculator = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_calculator, text="Калькулятор вероятностей")
        self._create_calculator_tab()

        # Вкладка 3: Симулятор
        self.tab_simulator = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_simulator, text="Симулятор")
        self._create_simulator_tab()

        # Вкладка 4: Статистика и графики
        self.tab_stats = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_stats, text="Статистика")
        self._create_stats_tab()

        # Вкладка 5: Гайд по рекомбинаторам
        self.tab_guide = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_guide, text="Гайд")
        self._create_guide_tab()

        # Вкладка 6: Помощник крафта
        self.tab_advisor = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_advisor, text="🎯 Помощник крафта")
        self._create_advisor_tab()

    def _create_setup_tab(self):
        """Создание вкладки настройки предметов"""
        # Разделяем на два фрейма для двух предметов
        left_frame = ttk.Frame(self.tab_setup)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(self.tab_setup)
        right_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        # Настройка Item 1
        self._create_item_setup(left_frame, "Предмет 1", 1)

        # Настройка Item 2
        self._create_item_setup(right_frame, "Предмет 2", 2)

    def _create_item_setup(self, parent, title, item_num):
        """Создание панели настройки предмета"""
        # Заголовок
        ttk.Label(parent, text=title, style='Title.TLabel').pack(pady=10)

        # Фрейм для базовых параметров
        basic_frame = ttk.LabelFrame(parent, text="Базовые параметры", padding=10)
        basic_frame.pack(fill='x', padx=5, pady=5)

        # Название
        ttk.Label(basic_frame, text="Название:").grid(row=0, column=0, sticky='w', pady=2)
        name_var = tk.StringVar(value=f"Item {item_num}")
        ttk.Entry(basic_frame, textvariable=name_var, width=30).grid(row=0, column=1, pady=2)

        # Класс предмета
        ttk.Label(basic_frame, text="Класс:").grid(row=1, column=0, sticky='w', pady=2)
        class_var = tk.StringVar()
        class_combo = ttk.Combobox(basic_frame, textvariable=class_var, width=28,
                                   values=[c.value for c in ItemClass])
        class_combo.grid(row=1, column=1, pady=2)
        class_combo.current(0)

        # Item Level
        ttk.Label(basic_frame, text="Item Level:").grid(row=2, column=0, sticky='w', pady=2)
        ilvl_var = tk.IntVar(value=85)
        ttk.Spinbox(basic_frame, from_=1, to=100, textvariable=ilvl_var, width=28).grid(row=2, column=1, pady=2)

        # Кнопки создания и импорта предмета
        button_container = ttk.Frame(basic_frame)
        button_container.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(button_container, text="Создать предмет",
                  command=lambda: self._create_item(item_num, name_var.get(),
                                                    class_var.get(), ilvl_var.get())).pack(side='left', padx=5)

        ttk.Button(button_container, text="Импорт из текста",
                  command=lambda: self._import_item_dialog(item_num)).pack(side='left', padx=5)

        # Фрейм для модов
        mods_frame = ttk.LabelFrame(parent, text="Модификаторы", padding=10)
        mods_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Кнопки добавления модов
        button_frame = ttk.Frame(mods_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(button_frame, text="Добавить префикс",
                  command=lambda: self._add_mod_dialog(item_num, ModType.PREFIX)).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Добавить суффикс",
                  command=lambda: self._add_mod_dialog(item_num, ModType.SUFFIX)).pack(side='left', padx=2)

        # Список модов
        mods_list = tk.Listbox(mods_frame, height=12)
        mods_list.pack(fill='both', expand=True, pady=5)

        # Кнопка удаления мода
        ttk.Button(mods_frame, text="Удалить выбранный мод",
                  command=lambda: self._remove_mod(item_num, mods_list)).pack(pady=5)

        # Сохраняем ссылки на виджеты
        if item_num == 1:
            self.item1_name_var = name_var
            self.item1_class_var = class_var
            self.item1_ilvl_var = ilvl_var
            self.item1_mods_list = mods_list
        else:
            self.item2_name_var = name_var
            self.item2_class_var = class_var
            self.item2_ilvl_var = ilvl_var
            self.item2_mods_list = mods_list

    def _create_calculator_tab(self):
        """Создание вкладки калькулятора"""
        # Фрейм для отображения предметов
        items_frame = ttk.LabelFrame(self.tab_calculator, text="Текущие предметы", padding=10)
        items_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Два текстовых виджета для отображения предметов
        left_text = scrolledtext.ScrolledText(items_frame, width=40, height=15, wrap=tk.WORD)
        left_text.pack(side='left', fill='both', expand=True, padx=5)

        right_text = scrolledtext.ScrolledText(items_frame, width=40, height=15, wrap=tk.WORD)
        right_text.pack(side='left', fill='both', expand=True, padx=5)

        self.calc_item1_text = left_text
        self.calc_item2_text = right_text

        # Кнопка расчета
        ttk.Button(self.tab_calculator, text="Рассчитать все варианты",
                  command=self._calculate_probabilities).pack(pady=10)

        # Результаты
        results_frame = ttk.LabelFrame(self.tab_calculator, text="Результаты расчетов", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.calc_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD)
        self.calc_results_text.pack(fill='both', expand=True)

    def _create_simulator_tab(self):
        """Создание вкладки симулятора"""
        # Фрейм настроек симуляции
        settings_frame = ttk.LabelFrame(self.tab_simulator, text="Настройки симуляции", padding=10)
        settings_frame.pack(fill='x', padx=5, pady=5)

        # Количество симуляций
        ttk.Label(settings_frame, text="Количество симуляций:").grid(row=0, column=0, sticky='w', pady=2)
        self.sim_count_var = tk.IntVar(value=1000)
        ttk.Spinbox(settings_frame, from_=1, to=100000, textvariable=self.sim_count_var,
                   width=20).grid(row=0, column=1, pady=2)

        # Кнопки управления
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Запустить симуляцию",
                  command=self._run_simulation).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Одна попытка",
                  command=self._single_simulation).pack(side='left', padx=5)

        # Результаты
        results_frame = ttk.LabelFrame(self.tab_simulator, text="Результаты симуляции", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.sim_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD)
        self.sim_results_text.pack(fill='both', expand=True)

    def _create_stats_tab(self):
        """Создание вкладки статистики"""
        # Текстовая статистика
        text_frame = ttk.LabelFrame(self.tab_stats, text="Статистика", padding=10)
        text_frame.pack(fill='x', padx=5, pady=5)

        self.stats_text = scrolledtext.ScrolledText(text_frame, height=10, wrap=tk.WORD)
        self.stats_text.pack(fill='both', expand=True)

        # Фрейм для графиков
        chart_frame = ttk.LabelFrame(self.tab_stats, text="Визуализация", padding=10)
        chart_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.chart_frame = chart_frame

    def _create_guide_tab(self):
        """Создание вкладки с гайдом по рекомбинаторам"""
        # Создаем ScrolledText для отображения гайда
        guide_text = scrolledtext.ScrolledText(self.tab_guide, wrap=tk.WORD,
                                               font=('Arial', 10), padx=10, pady=10)
        guide_text.pack(fill='both', expand=True)

        # Полный текст гайда
        guide_content = """
═══════════════════════════════════════════════════════════════════════════
                    ПОЛНЫЙ ГАЙД ПО РЕКОМБИНАТОРАМ POE
═══════════════════════════════════════════════════════════════════════════

📋 ОСНОВНЫЕ ПРАВИЛА РЕКОМБИНАЦИИ

1. СОВМЕСТИМОСТЬ ПРЕДМЕТОВ:
   • Предметы должны быть одного класса (оба кольца, оба меча и т.д.)
   • Нельзя рекомбинировать Corrupted или Mirrored предметы
   • Оба предмета должны быть Magic или Rare

2. ВЫБОР БАЗЫ:
   • Есть 50% шанс, что любой из двух предметов станет базой результата
   • Item Level результата = максимальный iLvl из двух предметов
   • Тип базы (например, Synthesised) сохраняется с базового предмета

3. ВЫБОР МОДОВ:
   • Префиксы и суффиксы обрабатываются отдельно
   • Из каждой группы модов можно выбрать только ОДИН мод
   • Максимум 3 префикса и 3 суффикса в результате
   • Fractured моды НЕ переносятся, но могут остаться на оригинальной базе

═══════════════════════════════════════════════════════════════════════════

📊 ТАБЛИЦА ВЕРОЯТНОСТЕЙ УСПЕХА

Начальные моды → Желаемый результат → Вероятность успеха

2 префикса → 2 префикса: 33%
4 префикса → 3 префикса: 31%
6 префиксов → 3 префикса: 13%

Формула вероятности успеха:
    Success Rate = 35% - (5% × кол-во модов) - (2% × сумма тиров) + бонусы

Где:
    • Базовый шанс: 35%
    • Штраф за моды: 5% за каждый выбранный мод
    • Штраф за тиры: 2% × (7 - значение тира), T1 = больше штраф
    • Бонус за малый пул: 5% × (6 - общее кол-во модов) если < 6

═══════════════════════════════════════════════════════════════════════════

⭐ ЭКСКЛЮЗИВНЫЕ МОДЫ (EXCLUSIVE MODS)

Эксклюзивные моды включают:
    • Essence моды
    • Beast Aspects
    • Breach/Incursion моды
    • Meta-моды (Can have 3 Crafted Modifiers)
    • Elevated Influenced моды
    • Delve моды
    • Veiled моды и крафты

ВАЖНОЕ ПРАВИЛО:
    Если выбран один эксклюзивный мод, все остальные эксклюзивные
    моды УДАЛЯЮТСЯ из пула! Но оставшиеся обычные моды переносятся.

ТЕХНИКА ИСПОЛЬЗОВАНИЯ:
    1. Создайте предмет с 2 желаемыми префиксами
    2. Добавьте 4 эксклюзивных мода крафтом
    3. Второй предмет: 1 желаемый префикс + 4 эксклюзивных
    4. При рекомбинации если выбран эксклюзивный мод, остальные
       удаляются, но 3 желаемых префикса остаются!

═══════════════════════════════════════════════════════════════════════════

🎯 МОДЫ NNN (NON-NATIVE NATURAL)

NNN моды - это моды которые не могут появиться на базе естественно:
    • ES моды на чистых Armour/Strength базах
    • Evasion моды на чистых ES/Intelligence базах
    • Suppression на базах без Evasion
    • Influenced моды на неинфлюенснутых базах

ИСПОЛЬЗОВАНИЕ:
    • Заполните один предмет NNN модами которые не нужны
    • Второй предмет с желаемыми модами
    • NNN моды не переносятся, увеличивая шанс переноса нужных!

ПРИМЕР:
    Предмет 1: T1 Life + PDR + 3 NNN мода (Intelligence, ES recharge, Max ES)
    Предмет 2: T1 Suppression + Armour/Evasion
    Результат: Высокий шанс получить все 4 желаемых мода!

═══════════════════════════════════════════════════════════════════════════

💡 ПРОДВИНУТЫЕ ТЕХНИКИ

1. БАЗОВАЯ РЕКОМБИНАЦИЯ (3 МОДА):
   • Накатайте Alterations на ~36 баз с нужными модами
   • Объедините 1-модные базы в 2-модные (шанс 33%)
   • Объедините 2-модные базы в 3-модные (шанс 31%)
   • В среднем нужно ~36 баз для одной 3-модной

2. ПРОДВИНУТАЯ РЕКОМБИНАЦИЯ (5 МОДОВ):
   • Создайте 2 базы: одна с 2P+2S, другая с 2P+2S
   • Добавьте эксклюзивные моды: 4 на первую базу, 3 на вторую
   • Объедините: если выбран exclusive, все желаемые моды переносятся!
   • Повторяйте с "неудачными" базами пока не получите 5 модов

3. ТЕХНИКА С ROG БАЗАМИ:
   • Используйте NNN моды на базах от Rog
   • Комбинируйте с вашей желаемой базой
   • Экономите Divine Orbs!

4. ПОВЫШЕНИЕ ITEM LEVEL:
   • Нужна iLvl 86 база? Объедините iLvl 84+ с любой iLvl 86+
   • Шанс 50/50 получить iLvl 86 на нужной базе!

═══════════════════════════════════════════════════════════════════════════

⚠️ ВАЖНЫЕ СОВЕТЫ

✓ Используйте Orb of Annulment для удаления нежелательных модов
✓ Используйте Regex (poe.re) для быстрого поиска нужных модов
✓ "Провальные" базы с хорошими модами можно использовать повторно!
✓ Заполняйте провальные базы эксклюзивными модами и пробуйте снова
✓ Не расстраивайтесь - это рандом, среднее значение попыток не гарантия

✗ НЕ крафтите 1-модные базы без второго мода (дороже в dust)
✗ НЕ забывайте про группы модов (только один мод из группы!)
✗ НЕ пытайтесь комбинировать два разных эксклюзивных мода
✗ НЕ игнорируйте NNN правила - используйте их!

═══════════════════════════════════════════════════════════════════════════

📖 ПРИМЕРЫ КРАФТА

ПРИМЕР 1: ФИЗИЧЕСКОЕ ОРУЖИЕ (3 ПРЕФИКСА)
    Цель: % Physical Damage + Flat Physical + Hybrid Physical

    Шаг 1: Накатайте ~36 баз с Alterations
    Шаг 2: Объедините 1-модные → 2-модные (нужно ~18 попыток)
    Шаг 3: Объедините 2-модные → 3-модные (нужно ~6 попыток)

    Итого: ~36 баз, ~1000 Alterations

ПРИМЕР 2: ИДЕАЛЬНЫЙ ДОСПЕХ (5 МОДОВ)
    Цель: T1 Flat ES + % ES + Hybrid ES + Suppression + Intelligence

    Шаг 1: База 1: 2P (Flat ES, % ES) + 1S (Suppression)
    Шаг 2: База 2: 2P (Flat ES, Hybrid ES) + 1S (Intelligence)
    Шаг 3: Заполните базу 1: добавьте 3 эксклюзивных крафта
    Шаг 4: Заполните базу 2: добавьте 4 эксклюзивных мода
    Шаг 5: Объедините! При выборе exclusive все 5 модов переносятся

═══════════════════════════════════════════════════════════════════════════

🎓 ИСТОЧНИКИ И БЛАГОДАРНОСТИ

Информация основана на:
    • Maxroll.gg Recombination Guide
    • Community testing и research
    • Reddit user /u/Butsicles

Удачи в крафте, Exile! 🔥
        """

        guide_text.insert(1.0, guide_content)
        guide_text.config(state='disabled')  # Только для чтения

    def _create_advisor_tab(self):
        """Создание вкладки помощника крафта"""
        # Главный контейнер с прокруткой
        main_canvas = tk.Canvas(self.tab_advisor)
        scrollbar = ttk.Scrollbar(self.tab_advisor, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Заголовок
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(title_frame, text="🎯 Помощник по крафту рекомбинаторов",
                 style='Title.TLabel').pack()
        ttk.Label(title_frame, text="Отметьте желаемые моды и получите оптимальную стратегию крафта",
                 font=('Arial', 10)).pack()

        # Секция выбора желаемых модов
        selection_frame = ttk.LabelFrame(scrollable_frame, text="Желаемые моды", padding=10)
        selection_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Создаем две колонки для префиксов и суффиксов
        cols_frame = ttk.Frame(selection_frame)
        cols_frame.pack(fill='both', expand=True)

        # Префиксы
        prefix_frame = ttk.LabelFrame(cols_frame, text="Префиксы (макс 3)", padding=10)
        prefix_frame.pack(side='left', fill='both', expand=True, padx=5)

        # Кнопка добавления префикса
        ttk.Button(prefix_frame, text="+ Добавить префикс",
                  command=lambda: self._add_desired_mod_dialog(ModType.PREFIX)).pack(pady=5)

        # Список желаемых префиксов
        self.desired_prefixes_listbox = tk.Listbox(prefix_frame, height=8)
        self.desired_prefixes_listbox.pack(fill='both', expand=True, pady=5)

        ttk.Button(prefix_frame, text="Удалить выбранный",
                  command=lambda: self._remove_desired_mod(ModType.PREFIX)).pack()

        # Суффиксы
        suffix_frame = ttk.LabelFrame(cols_frame, text="Суффиксы (макс 3)", padding=10)
        suffix_frame.pack(side='left', fill='both', expand=True, padx=5)

        # Кнопка добавления суффикса
        ttk.Button(suffix_frame, text="+ Добавить суффикс",
                  command=lambda: self._add_desired_mod_dialog(ModType.SUFFIX)).pack(pady=5)

        # Список желаемых суффиксов
        self.desired_suffixes_listbox = tk.Listbox(suffix_frame, height=8)
        self.desired_suffixes_listbox.pack(fill='both', expand=True, pady=5)

        ttk.Button(suffix_frame, text="Удалить выбранный",
                  command=lambda: self._remove_desired_mod(ModType.SUFFIX)).pack()

        # Хранилища для желаемых модов
        self.desired_prefixes: List[Mod] = []
        self.desired_suffixes: List[Mod] = []

        # Кнопка анализа
        analyze_btn_frame = ttk.Frame(scrollable_frame)
        analyze_btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(analyze_btn_frame, text="🔍 Проанализировать и получить рекомендации",
                  command=self._analyze_craft,
                  style='TButton').pack(pady=5)

        # Результаты анализа
        results_frame = ttk.LabelFrame(scrollable_frame, text="Результаты анализа", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.advisor_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD,
                                                              height=25, font=('Consolas', 10))
        self.advisor_results_text.pack(fill='both', expand=True)

    def _add_desired_mod_dialog(self, mod_type: ModType):
        """Диалог добавления желаемого мода"""
        # Проверяем лимиты
        if mod_type == ModType.PREFIX and len(self.desired_prefixes) >= 3:
            messagebox.showwarning("Внимание", "Максимум 3 префикса")
            return
        if mod_type == ModType.SUFFIX and len(self.desired_suffixes) >= 3:
            messagebox.showwarning("Внимание", "Максимум 3 суффикса")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Добавить желаемый {mod_type.value}")
        dialog.geometry("400x450")

        # Название мода
        ttk.Label(dialog, text="Название мода:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=40).pack(pady=5)

        # Группа мода
        ttk.Label(dialog, text="Группа мода (например, 'Life', 'ColdResistance'):").pack(pady=5)
        group_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=group_var, width=40).pack(pady=5)

        # Тир
        ttk.Label(dialog, text="Желаемый тир:").pack(pady=5)
        tier_var = tk.StringVar()
        ttk.Combobox(dialog, textvariable=tier_var, values=[t.name for t in ModTier],
                    width=38).pack(pady=5)
        tier_var.set("T1")

        # Эксклюзивный?
        exclusive_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Эксклюзивный мод (essence, fossil, etc.)",
                       variable=exclusive_var).pack(pady=5)

        # Информация
        info_label = ttk.Label(dialog,
                              text="💡 Укажите моды которые вы хотите получить\nв финальном предмете",
                              foreground='blue')
        info_label.pack(pady=10)

        def add_mod():
            if not name_var.get() or not group_var.get():
                messagebox.showwarning("Внимание", "Заполните название и группу")
                return

            mod = Mod(
                name=name_var.get(),
                mod_type=mod_type,
                tier=ModTier[tier_var.get()],
                mod_group=group_var.get(),
                is_exclusive=exclusive_var.get()
            )

            if mod_type == ModType.PREFIX:
                self.desired_prefixes.append(mod)
                self.desired_prefixes_listbox.insert(tk.END, str(mod))
            else:
                self.desired_suffixes.append(mod)
                self.desired_suffixes_listbox.insert(tk.END, str(mod))

            dialog.destroy()

        ttk.Button(dialog, text="Добавить", command=add_mod).pack(pady=20)

    def _remove_desired_mod(self, mod_type: ModType):
        """Удаление желаемого мода"""
        if mod_type == ModType.PREFIX:
            selection = self.desired_prefixes_listbox.curselection()
            if selection:
                idx = selection[0]
                self.desired_prefixes.pop(idx)
                self.desired_prefixes_listbox.delete(idx)
        else:
            selection = self.desired_suffixes_listbox.curselection()
            if selection:
                idx = selection[0]
                self.desired_suffixes.pop(idx)
                self.desired_suffixes_listbox.delete(idx)

    def _analyze_craft(self):
        """Анализ и вывод рекомендаций"""
        if not self.desired_prefixes and not self.desired_suffixes:
            messagebox.showwarning("Внимание", "Добавьте желаемые моды для анализа")
            return

        # Валидация
        is_valid, issues = self.advisor.validate_desired_combination(
            self.desired_prefixes + self.desired_suffixes
        )

        # Получаем рекомендации
        recommendation = self.advisor.analyze_desired_outcome(
            self.desired_prefixes,
            self.desired_suffixes
        )

        # Форматируем результат
        result_text = self._format_recommendation(recommendation, is_valid, issues)

        # Выводим
        self.advisor_results_text.delete(1.0, tk.END)
        self.advisor_results_text.insert(1.0, result_text)

    def _format_recommendation(self, rec, is_valid, issues) -> str:
        """Форматирование рекомендации для отображения"""
        lines = []
        lines.append("=" * 80)
        lines.append("АНАЛИЗ ЖЕЛАЕМОГО РЕЗУЛЬТАТА")
        lines.append("=" * 80)
        lines.append("")

        # Желаемые моды
        lines.append("Вы хотите получить:")
        lines.append("")
        lines.append(f"Префиксы ({len(self.desired_prefixes)}):")
        for mod in self.desired_prefixes:
            lines.append(f"  • {mod}")
        lines.append("")
        lines.append(f"Суффиксы ({len(self.desired_suffixes)}):")
        for mod in self.desired_suffixes:
            lines.append(f"  • {mod}")
        lines.append("")

        # Валидация
        if not is_valid:
            lines.append("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ:")
            for issue in issues:
                lines.append(f"  • {issue}")
            lines.append("")

        lines.append("=" * 80)
        lines.append(f"РЕКОМЕНДУЕМАЯ СТРАТЕГИЯ: {rec.strategy.value}")
        lines.append("=" * 80)
        lines.append("")

        # Сложность
        feasibility_emoji = {
            "Легко": "✅",
            "Средне": "⚠️",
            "Сложно": "🔶",
            "Очень сложно": "🔴",
            "Невозможно": "❌"
        }
        emoji = feasibility_emoji.get(rec.feasibility, "")
        lines.append(f"{emoji} Сложность: {rec.feasibility}")
        lines.append(f"📊 Вероятность успеха: {rec.success_probability:.1%}")
        lines.append(f"🎲 Среднее кол-во попыток: {rec.average_attempts}")
        lines.append("")

        # Предупреждения
        if rec.warnings:
            lines.append("⚠️  ПРЕДУПРЕЖДЕНИЯ:")
            for warning in rec.warnings:
                lines.append(f"  {warning}")
            lines.append("")

        # Пошаговый план
        lines.append("=" * 80)
        lines.append("ПОШАГОВЫЙ ПЛАН:")
        lines.append("=" * 80)
        lines.append("")
        for step in rec.steps:
            lines.append(step)
        lines.append("")

        # Ресурсы
        if rec.estimated_cost:
            lines.append("=" * 80)
            lines.append("НЕОБХОДИМЫЕ РЕСУРСЫ (примерно):")
            lines.append("=" * 80)
            for resource, amount in rec.estimated_cost.items():
                if isinstance(amount, (int, float)):
                    lines.append(f"  • {resource}: {amount}")
                else:
                    lines.append(f"  • {resource}: {amount}")
            lines.append("")

        # Советы
        if rec.tips:
            lines.append("💡 ПОЛЕЗНЫЕ СОВЕТЫ:")
            for tip in rec.tips:
                lines.append(f"  {tip}")
            lines.append("")

        lines.append("=" * 80)
        lines.append("Удачного крафта! Используйте симулятор для проверки вероятностей.")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _create_item(self, item_num, name, item_class_str, ilvl):
        """Создание предмета"""
        try:
            item_class = ItemClass[item_class_str.upper().replace(" ", "_")]

            item = Item(
                name=name,
                item_class=item_class,
                item_level=ilvl
            )

            if item_num == 1:
                self.item1 = item
                self.current_mods_item1 = []
                messagebox.showinfo("Успех", f"Предмет 1 создан: {name}")
            else:
                self.item2 = item
                self.current_mods_item2 = []
                messagebox.showinfo("Успех", f"Предмет 2 создан: {name}")

            self._update_displays()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать предмет: {str(e)}")

    def _import_item_dialog(self, item_num):
        """Диалог импорта предмета из текста"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Импорт предмета {item_num} из текста")
        dialog.geometry("700x600")

        # Инструкция
        ttk.Label(dialog, text="Вставьте текст предмета из игры (Ctrl+C в игре):",
                 font=('Arial', 10, 'bold')).pack(pady=10)

        # Текстовое поле для вставки
        text_widget = scrolledtext.ScrolledText(dialog, width=80, height=25, wrap=tk.WORD,
                                                font=('Consolas', 9))
        text_widget.pack(padx=10, pady=5, fill='both', expand=True)

        # Пример для помощи
        example_text = """Пример формата:
Класс предмета: Кольца
Редкость: Редкий
Громадный захват
Кольцо без камня
--------
Уровень предмета: 86
--------
Имеет 1 гнездо (implicit)
--------
+29% к сопротивлению хаосу (fractured)
+37 к максимуму энергетического щита
+48% к сопротивлению холоду
        """
        text_widget.insert(1.0, example_text)

        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        def import_item():
            text = text_widget.get(1.0, tk.END)
            parser = ItemParser()
            item = parser.parse_item_text(text)

            if item:
                # Устанавливаем предмет
                if item_num == 1:
                    self.item1 = item
                    self.current_mods_item1 = item.all_mods.copy()
                    # Обновляем поля в GUI
                    self.item1_name_var.set(item.name)
                    self.item1_class_var.set(item.item_class.value)
                    self.item1_ilvl_var.set(item.item_level)
                else:
                    self.item2 = item
                    self.current_mods_item2 = item.all_mods.copy()
                    # Обновляем поля в GUI
                    self.item2_name_var.set(item.name)
                    self.item2_class_var.set(item.item_class.value)
                    self.item2_ilvl_var.set(item.item_level)

                self._update_mod_lists()
                self._update_displays()

                messagebox.showinfo("Успех",
                                  f"Предмет импортирован!\n\n"
                                  f"Название: {item.name}\n"
                                  f"Класс: {item.item_class.value}\n"
                                  f"iLvl: {item.item_level}\n"
                                  f"Модов: {item.total_mod_count}\n"
                                  f"Fractured: {'Да' if item.has_fractured_mod() else 'Нет'}")
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка",
                                   "Не удалось распарсить предмет.\n"
                                   "Проверьте формат текста.")

        ttk.Button(button_frame, text="Импортировать",
                  command=import_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена",
                  command=dialog.destroy).pack(side='left', padx=5)

    def _add_mod_dialog(self, item_num, mod_type):
        """Диалог добавления мода"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Добавить {mod_type.value}")
        dialog.geometry("400x400")

        # Название мода
        ttk.Label(dialog, text="Название мода:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=40).pack(pady=5)

        # Группа мода
        ttk.Label(dialog, text="Группа мода (например, 'Life', 'Strength'):").pack(pady=5)
        group_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=group_var, width=40).pack(pady=5)

        # Тир
        ttk.Label(dialog, text="Тир:").pack(pady=5)
        tier_var = tk.StringVar()
        ttk.Combobox(dialog, textvariable=tier_var, values=[t.name for t in ModTier],
                    width=38).pack(pady=5)
        tier_var.set("T1")

        # Значение (опционально)
        ttk.Label(dialog, text="Значение (опционально):").pack(pady=5)
        value_var = tk.IntVar(value=0)
        ttk.Spinbox(dialog, from_=0, to=999, textvariable=value_var, width=38).pack(pady=5)

        # Эксклюзивный мод
        exclusive_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Эксклюзивный мод (essence, fossil)",
                       variable=exclusive_var).pack(pady=5)

        # Кнопка добавления
        def add_mod():
            if not name_var.get() or not group_var.get():
                messagebox.showwarning("Внимание", "Заполните название и группу мода")
                return

            mod = Mod(
                name=name_var.get(),
                mod_type=mod_type,
                tier=ModTier[tier_var.get()],
                mod_group=group_var.get(),
                is_exclusive=exclusive_var.get(),
                current_value=value_var.get() if value_var.get() > 0 else None
            )

            if item_num == 1:
                if mod_type == ModType.PREFIX:
                    if len([m for m in self.current_mods_item1 if m.mod_type == ModType.PREFIX]) >= 3:
                        messagebox.showwarning("Внимание", "Максимум 3 префикса")
                        return
                    if self.item1:
                        self.item1.prefixes.append(mod)
                else:
                    if len([m for m in self.current_mods_item1 if m.mod_type == ModType.SUFFIX]) >= 3:
                        messagebox.showwarning("Внимание", "Максимум 3 суффикса")
                        return
                    if self.item1:
                        self.item1.suffixes.append(mod)
                self.current_mods_item1.append(mod)
            else:
                if mod_type == ModType.PREFIX:
                    if len([m for m in self.current_mods_item2 if m.mod_type == ModType.PREFIX]) >= 3:
                        messagebox.showwarning("Внимание", "Максимум 3 префикса")
                        return
                    if self.item2:
                        self.item2.prefixes.append(mod)
                else:
                    if len([m for m in self.current_mods_item2 if m.mod_type == ModType.SUFFIX]) >= 3:
                        messagebox.showwarning("Внимание", "Максимум 3 суффикса")
                        return
                    if self.item2:
                        self.item2.suffixes.append(mod)
                self.current_mods_item2.append(mod)

            self._update_mod_lists()
            self._update_displays()
            dialog.destroy()

        ttk.Button(dialog, text="Добавить мод", command=add_mod).pack(pady=20)

    def _remove_mod(self, item_num, listbox):
        """Удаление выбранного мода"""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите мод для удаления")
            return

        idx = selection[0]

        if item_num == 1 and self.item1:
            mod = self.current_mods_item1[idx]
            if mod.mod_type == ModType.PREFIX:
                self.item1.prefixes.remove(mod)
            else:
                self.item1.suffixes.remove(mod)
            self.current_mods_item1.pop(idx)
        elif item_num == 2 and self.item2:
            mod = self.current_mods_item2[idx]
            if mod.mod_type == ModType.PREFIX:
                self.item2.prefixes.remove(mod)
            else:
                self.item2.suffixes.remove(mod)
            self.current_mods_item2.pop(idx)

        self._update_mod_lists()
        self._update_displays()

    def _update_mod_lists(self):
        """Обновление списков модов"""
        # Обновляем Item 1
        self.item1_mods_list.delete(0, tk.END)
        for mod in self.current_mods_item1:
            self.item1_mods_list.insert(tk.END, str(mod))

        # Обновляем Item 2
        self.item2_mods_list.delete(0, tk.END)
        for mod in self.current_mods_item2:
            self.item2_mods_list.insert(tk.END, str(mod))

    def _update_displays(self):
        """Обновление отображения предметов во всех вкладках"""
        # Обновляем в калькуляторе
        self.calc_item1_text.delete(1.0, tk.END)
        self.calc_item2_text.delete(1.0, tk.END)

        if self.item1:
            self.calc_item1_text.insert(1.0, str(self.item1))
        if self.item2:
            self.calc_item2_text.insert(1.0, str(self.item2))

    def _calculate_probabilities(self):
        """Расчет вероятностей всех исходов"""
        if not self.item1 or not self.item2:
            messagebox.showwarning("Внимание", "Создайте оба предмета")
            return

        # Проверка совместимости
        can_combine, reason = self.item1.can_recombine_with(self.item2)
        if not can_combine:
            messagebox.showerror("Ошибка", f"Невозможно рекомбинировать: {reason}")
            return

        # Анализ всех исходов
        outcomes = self.calculator.analyze_all_outcomes(self.item1, self.item2)

        # Статистика
        stats = self.calculator.get_statistics_summary(outcomes)

        # Вывод результатов
        self.calc_results_text.delete(1.0, tk.END)

        result_text = "=" * 80 + "\n"
        result_text += "АНАЛИЗ ВСЕХ ВОЗМОЖНЫХ ИСХОДОВ РЕКОМБИНАЦИИ\n"
        result_text += "=" * 80 + "\n\n"

        result_text += f"Всего возможных исходов: {stats['total_outcomes']}\n"
        result_text += f"Средний шанс успеха: {stats['average_success_rate']:.2%}\n"
        result_text += f"Вероятность получить ≥2 префикса и ≥2 суффикса: {stats['probability_2_2_or_better']:.2%}\n"
        result_text += f"Вероятность получить 3 префикса и 3 суффикса: {stats['probability_3_3']:.2%}\n"
        result_text += "\n" + "-" * 80 + "\n"
        result_text += "ТОП-20 НАИБОЛЕЕ ВЕРОЯТНЫХ ИСХОДОВ:\n"
        result_text += "-" * 80 + "\n\n"

        for i, outcome in enumerate(outcomes[:20], 1):
            result_text += f"\n#{i}. {outcome['prefix_count']}P + {outcome['suffix_count']}S "
            result_text += f"(общая вероятность: {outcome['combined_probability']:.4%})\n"
            result_text += f"  Шанс выбора модов: {outcome['selection_probability']:.4%}\n"
            result_text += f"  Шанс успеха крафта: {outcome['success_probability']:.2%}\n"

            if outcome['prefixes']:
                result_text += "  Префиксы:\n"
                for mod in outcome['prefixes']:
                    result_text += f"    • {mod}\n"

            if outcome['suffixes']:
                result_text += "  Суффиксы:\n"
                for mod in outcome['suffixes']:
                    result_text += f"    • {mod}\n"

        self.calc_results_text.insert(1.0, result_text)

    def _single_simulation(self):
        """Одна попытка симуляции"""
        if not self.item1 or not self.item2:
            messagebox.showwarning("Внимание", "Создайте оба предмета")
            return

        result = self.simulator.simulate_single_recombination(self.item1, self.item2)

        self.sim_results_text.delete(1.0, tk.END)

        result_text = "=" * 80 + "\n"
        result_text += "РЕЗУЛЬТАТ ОДНОЙ РЕКОМБИНАЦИИ\n"
        result_text += "=" * 80 + "\n\n"
        result_text += str(result) + "\n"

        self.sim_results_text.insert(1.0, result_text)

    def _run_simulation(self):
        """Запуск множественной симуляции"""
        if not self.item1 or not self.item2:
            messagebox.showwarning("Внимание", "Создайте оба предмета")
            return

        num_sims = self.sim_count_var.get()

        results = self.simulator.simulate_multiple_recombinations(
            self.item1, self.item2, num_sims
        )

        # Вывод результатов
        self.sim_results_text.delete(1.0, tk.END)

        result_text = "=" * 80 + "\n"
        result_text += f"РЕЗУЛЬТАТЫ {num_sims} СИМУЛЯЦИЙ\n"
        result_text += "=" * 80 + "\n\n"

        result_text += f"Успехов: {results['successes']} ({results['success_rate']:.2%})\n"
        result_text += f"Провалов: {results['failures']}\n"
        result_text += f"Среднее кол-во префиксов: {results['average_prefixes']:.2f}\n"
        result_text += f"Среднее кол-во суффиксов: {results['average_suffixes']:.2f}\n\n"

        result_text += "-" * 80 + "\n"
        result_text += "РАСПРЕДЕЛЕНИЕ РЕЗУЛЬТАТОВ (Префиксы x Суффиксы):\n"
        result_text += "-" * 80 + "\n\n"

        for (p_count, s_count), count in sorted(results['results_distribution'].items()):
            percentage = (count / results['successes']) * 100 if results['successes'] > 0 else 0
            result_text += f"{p_count}P x {s_count}S: {count} раз ({percentage:.2f}%)\n"

        self.sim_results_text.insert(1.0, result_text)

        # Обновляем статистику
        self._update_statistics(results)

    def _update_statistics(self, results):
        """Обновление вкладки статистики"""
        # Текстовая статистика
        self.stats_text.delete(1.0, tk.END)

        stats_text = "СТАТИСТИКА ПОСЛЕДНЕЙ СИМУЛЯЦИИ\n"
        stats_text += "=" * 60 + "\n\n"
        stats_text += f"Всего симуляций: {results['total_simulations']}\n"
        stats_text += f"Успешных: {results['successes']}\n"
        stats_text += f"Провалов: {results['failures']}\n"
        stats_text += f"Процент успеха: {results['success_rate']:.2%}\n\n"

        self.stats_text.insert(1.0, stats_text)

        # Визуализация
        self._create_charts(results)

    def _create_charts(self, results):
        """Создание графиков"""
        # Очищаем предыдущие графики
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Создаем фигуру с графиками
        fig = Figure(figsize=(12, 6))

        # График 1: Pie chart успехов/провалов
        ax1 = fig.add_subplot(121)
        sizes = [results['successes'], results['failures']]
        labels = ['Успехи', 'Провалы']
        colors = ['#00ff00', '#ff0000']
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Соотношение успехов и провалов')

        # График 2: Bar chart распределения результатов
        ax2 = fig.add_subplot(122)
        distribution = results['results_distribution']
        labels = [f"{p}P x {s}S" for p, s in sorted(distribution.keys())]
        values = [distribution[k] for k in sorted(distribution.keys())]

        ax2.bar(labels, values, color='#d4af37')
        ax2.set_title('Распределение результатов')
        ax2.set_xlabel('Префиксы x Суффиксы')
        ax2.set_ylabel('Количество')
        ax2.tick_params(axis='x', rotation=45)

        fig.tight_layout()

        # Встраиваем в tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _clear_all(self):
        """Очистка всех данных"""
        self.item1 = None
        self.item2 = None
        self.current_mods_item1 = []
        self.current_mods_item2 = []
        self.simulator.clear_history()

        self._update_mod_lists()
        self._update_displays()

        self.calc_results_text.delete(1.0, tk.END)
        self.sim_results_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)

        messagebox.showinfo("Очистка", "Все данные очищены")

    def _show_instructions(self):
        """Показать инструкцию"""
        instructions = """
ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ СИМУЛЯТОРА РЕКОМБИНАТОРОВ

1. НАСТРОЙКА ПРЕДМЕТОВ:
   - Создайте два предмета на вкладке "Настройка предметов"
   - Укажите название, класс и item level
   - Добавьте модификаторы (префиксы и суффиксы)
   - Максимум 3 префикса и 3 суффикса на предмет

2. КАЛЬКУЛЯТОР ВЕРОЯТНОСТЕЙ:
   - Переключитесь на вкладку "Калькулятор вероятностей"
   - Нажмите "Рассчитать все варианты"
   - Увидите все возможные исходы и их вероятности

3. СИМУЛЯТОР:
   - На вкладке "Симулятор" можно запустить симуляции
   - "Одна попытка" - единичная рекомбинация
   - "Запустить симуляцию" - множественные попытки
   - Результаты отображаются в текстовом виде

4. СТАТИСТИКА:
   - На вкладке "Статистика" видны графики
   - Pie chart показывает соотношение успехов/провалов
   - Bar chart показывает распределение результатов

ВАЖНЫЕ ПРАВИЛА:
• Предметы должны быть одного класса
• Нельзя рекомбинировать corrupted предметы
• Из одной группы модов можно выбрать только один
• Максимум 3 префикса и 3 суффикса в результате
• Эксклюзивные моды (essence, fossil) имеют ограничения
        """

        msg_box = tk.Toplevel(self.root)
        msg_box.title("Инструкция")
        msg_box.geometry("700x600")

        text = scrolledtext.ScrolledText(msg_box, wrap=tk.WORD, font=('Arial', 10))
        text.pack(fill='both', expand=True, padx=10, pady=10)
        text.insert(1.0, instructions)
        text.config(state='disabled')

    def _show_about(self):
        """О программе"""
        about_text = """
PoE Recombinator Simulator v1.0

Симулятор рекомбинаторов Path of Exile

Функции:
• Расчет вероятностей рекомбинации
• Симуляция крафта
• Визуализация результатов
• Статистический анализ

Основано на механиках PoE 3.26+

Создано для помощи в понимании механик
рекомбинаторов и планировании крафта.
        """
        messagebox.showinfo("О программе", about_text)


def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = RecombinatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
