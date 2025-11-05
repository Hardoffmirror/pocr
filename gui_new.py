"""
Новый компактный GUI для симулятора рекомбинаторов Path of Exile
Все в одном окне - удобно, наглядно, красиво
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from models import Item, Mod, ModType, ModTier, ItemClass
from simulator import RecombinatorSimulator
from calculator import RecombinatorCalculator
from item_parser import ItemParser
from craft_advisor import CraftAdvisor, CraftStrategy


class CompactRecombinatorGUI:
    """Компактный интерфейс в одном окне"""

    def __init__(self, root):
        self.root = root
        self.root.title("PoE Recombinator - Craft Advisor")
        self.root.geometry("1600x900")
        self.root.configure(bg='#1a1410')

        # Сервисы
        self.simulator = RecombinatorSimulator()
        self.calculator = RecombinatorCalculator()
        self.advisor = CraftAdvisor()
        self.parser = ItemParser()

        # Данные
        self.item1: Optional[Item] = None
        self.item2: Optional[Item] = None
        self.desired_prefixes: List[Mod] = []
        self.desired_suffixes: List[Mod] = []

        # Настройка стилей
        self._setup_styles()

        # Создание интерфейса
        self._create_interface()

    def _setup_styles(self):
        """Настройка стилей в стиле PoE"""
        style = ttk.Style()
        style.theme_use('clam')

        # Цвета PoE
        bg_dark = '#1a1410'
        bg_medium = '#2a2420'
        fg_gold = '#c8aa6e'
        fg_rare = '#ffff77'
        fg_magic = '#8888ff'

        # Стили для фреймов
        style.configure('Dark.TFrame', background=bg_dark)
        style.configure('Medium.TFrame', background=bg_medium)

        # Стили для кнопок
        style.configure('Gold.TButton',
                       background=bg_medium,
                       foreground=fg_gold,
                       borderwidth=2,
                       relief='raised',
                       font=('Arial', 10, 'bold'))
        style.map('Gold.TButton',
                 background=[('active', '#3a3430')])

        # Стили для меток
        style.configure('Title.TLabel',
                       background=bg_dark,
                       foreground=fg_gold,
                       font=('Arial', 14, 'bold'))
        style.configure('Subtitle.TLabel',
                       background=bg_medium,
                       foreground=fg_rare,
                       font=('Arial', 11, 'bold'))
        style.configure('Normal.TLabel',
                       background=bg_medium,
                       foreground='#d0d0d0',
                       font=('Arial', 10))
        style.configure('Magic.TLabel',
                       background=bg_medium,
                       foreground=fg_magic,
                       font=('Arial', 10))

    def _create_interface(self):
        """Создание главного интерфейса"""
        # Главный контейнер с padding
        main_container = ttk.Frame(self.root, style='Dark.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок приложения
        header = ttk.Frame(main_container, style='Dark.TFrame')
        header.pack(fill=tk.X, pady=(0, 10))

        title = ttk.Label(header,
                         text="⚔️ POE RECOMBINATOR CRAFT ADVISOR ⚔️",
                         style='Title.TLabel')
        title.pack()

        # Основная компоновка: 3 колонки
        content = ttk.Frame(main_container, style='Dark.TFrame')
        content.pack(fill=tk.BOTH, expand=True)

        # Левая колонка - Предметы (30%)
        left_panel = self._create_items_panel(content)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))

        # Центральная колонка - Желаемые моды и Стратегия (40%)
        center_panel = self._create_strategy_panel(content)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Правая колонка - Ресурсы и Вероятности (30%)
        right_panel = self._create_results_panel(content)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(5, 0))

    def _create_items_panel(self, parent):
        """Панель для добавления предметов"""
        panel = ttk.Frame(parent, style='Medium.TFrame', width=350)
        panel.pack_propagate(False)

        # Заголовок
        title = ttk.Label(panel, text="📦 ПРЕДМЕТЫ", style='Subtitle.TLabel')
        title.pack(pady=10)

        # Предмет 1
        item1_frame = ttk.LabelFrame(panel, text="Предмет 1", style='Medium.TFrame')
        item1_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(item1_frame,
                  text="📋 Импорт из игры",
                  style='Gold.TButton',
                  command=lambda: self._import_item(1)).pack(pady=5)

        ttk.Button(item1_frame,
                  text="➕ Добавить моды",
                  command=lambda: self._add_mods_manually(1)).pack(pady=5)

        self.item1_info = tk.Text(item1_frame,
                                  height=8,
                                  width=35,
                                  bg='#2a2420',
                                  fg='#8888ff',
                                  font=('Courier', 9))
        self.item1_info.pack(padx=5, pady=5)
        self.item1_info.insert('1.0', 'Предмет не добавлен')
        self.item1_info.config(state='disabled')

        # Предмет 2
        item2_frame = ttk.LabelFrame(panel, text="Предмет 2", style='Medium.TFrame')
        item2_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(item2_frame,
                  text="📋 Импорт из игры",
                  style='Gold.TButton',
                  command=lambda: self._import_item(2)).pack(pady=5)

        ttk.Button(item2_frame,
                  text="➕ Добавить моды",
                  command=lambda: self._add_mods_manually(2)).pack(pady=5)

        self.item2_info = tk.Text(item2_frame,
                                  height=8,
                                  width=35,
                                  bg='#2a2420',
                                  fg='#8888ff',
                                  font=('Courier', 9))
        self.item2_info.pack(padx=5, pady=5)
        self.item2_info.insert('1.0', 'Предмет не добавлен')
        self.item2_info.config(state='disabled')

        # Кнопка расчета
        calc_frame = ttk.Frame(panel, style='Medium.TFrame')
        calc_frame.pack(fill=tk.X, padx=10, pady=20)

        ttk.Button(calc_frame,
                  text="🎯 Рассчитать рекомбинацию",
                  style='Gold.TButton',
                  command=self._calculate_basic).pack(fill=tk.X)

        return panel

    def _create_strategy_panel(self, parent):
        """Центральная панель - желаемые моды и визуализация стратегии"""
        panel = ttk.Frame(parent, style='Medium.TFrame')

        # Заголовок
        title = ttk.Label(panel, text="🎯 ЖЕЛАЕМЫЙ РЕЗУЛЬТАТ И СТРАТЕГИЯ", style='Subtitle.TLabel')
        title.pack(pady=10)

        # Разделение на верх (желаемые моды) и низ (стратегия)
        desired_frame = ttk.LabelFrame(panel, text="Желаемые моды", style='Medium.TFrame')
        desired_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки добавления модов
        btn_frame = ttk.Frame(desired_frame, style='Medium.TFrame')
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame,
                  text="➕ Префикс",
                  command=lambda: self._add_desired_mod(ModType.PREFIX)).pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame,
                  text="➕ Суффикс",
                  command=lambda: self._add_desired_mod(ModType.SUFFIX)).pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame,
                  text="🗑️ Очистить",
                  command=self._clear_desired_mods).pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame,
                  text="🎲 АНАЛИЗ",
                  style='Gold.TButton',
                  command=self._analyze_craft).pack(side=tk.LEFT, padx=20)

        # Список желаемых модов
        mods_display = ttk.Frame(desired_frame, style='Medium.TFrame')
        mods_display.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(mods_display, text="Префиксы:", style='Magic.TLabel').grid(row=0, column=0, sticky='w')
        self.prefix_list = tk.Listbox(mods_display,
                                      height=3,
                                      bg='#2a2420',
                                      fg='#8888ff',
                                      font=('Courier', 9))
        self.prefix_list.grid(row=1, column=0, sticky='ew', padx=(0, 5))

        ttk.Label(mods_display, text="Суффиксы:", style='Magic.TLabel').grid(row=0, column=1, sticky='w')
        self.suffix_list = tk.Listbox(mods_display,
                                      height=3,
                                      bg='#2a2420',
                                      fg='#ffff77',
                                      font=('Courier', 9))
        self.suffix_list.grid(row=1, column=1, sticky='ew', padx=(5, 0))

        mods_display.columnconfigure(0, weight=1)
        mods_display.columnconfigure(1, weight=1)

        # Визуализация стратегии
        strategy_frame = ttk.LabelFrame(panel, text="Визуальная стратегия", style='Medium.TFrame')
        strategy_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Canvas для matplotlib
        self.strategy_canvas_frame = ttk.Frame(strategy_frame, style='Medium.TFrame')
        self.strategy_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Начальный текст
        self.strategy_text = tk.Text(self.strategy_canvas_frame,
                                     bg='#2a2420',
                                     fg='#c8aa6e',
                                     font=('Courier', 10),
                                     wrap=tk.WORD)
        self.strategy_text.pack(fill=tk.BOTH, expand=True)
        self.strategy_text.insert('1.0', 'Добавьте желаемые моды и нажмите "АНАЛИЗ" для получения рекомендации')
        self.strategy_text.config(state='disabled')

        return panel

    def _create_results_panel(self, parent):
        """Правая панель - результаты, ресурсы, цены"""
        panel = ttk.Frame(parent, style='Medium.TFrame', width=350)
        panel.pack_propagate(False)

        # Заголовок
        title = ttk.Label(panel, text="💰 РЕСУРСЫ И ВЕРОЯТНОСТИ", style='Subtitle.TLabel')
        title.pack(pady=10)

        # Вероятность успеха
        prob_frame = ttk.LabelFrame(panel, text="Вероятность", style='Medium.TFrame')
        prob_frame.pack(fill=tk.X, padx=10, pady=5)

        self.prob_canvas = tk.Canvas(prob_frame, height=100, bg='#2a2420', highlightthickness=0)
        self.prob_canvas.pack(fill=tk.X, padx=10, pady=10)

        self.prob_label = ttk.Label(prob_frame, text="---%", style='Title.TLabel')
        self.prob_label.pack(pady=5)

        # Попытки
        attempts_frame = ttk.LabelFrame(panel, text="Попытки", style='Medium.TFrame')
        attempts_frame.pack(fill=tk.X, padx=10, pady=5)

        self.attempts_label = ttk.Label(attempts_frame,
                                        text="В среднем: ---",
                                        style='Subtitle.TLabel')
        self.attempts_label.pack(pady=10)

        # Стратегия
        strategy_type_frame = ttk.LabelFrame(panel, text="Тип стратегии", style='Medium.TFrame')
        strategy_type_frame.pack(fill=tk.X, padx=10, pady=5)

        self.strategy_type_label = ttk.Label(strategy_type_frame,
                                             text="---",
                                             style='Magic.TLabel',
                                             wraplength=300)
        self.strategy_type_label.pack(pady=10)

        # Ресурсы
        resources_frame = ttk.LabelFrame(panel, text="Необходимые ресурсы", style='Medium.TFrame')
        resources_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.resources_text = tk.Text(resources_frame,
                                      height=12,
                                      bg='#2a2420',
                                      fg='#ffff77',
                                      font=('Courier', 9))
        self.resources_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.resources_text.insert('1.0', 'Ожидание анализа...')
        self.resources_text.config(state='disabled')

        # Сложность
        difficulty_frame = ttk.Frame(panel, style='Medium.TFrame')
        difficulty_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(difficulty_frame, text="Сложность:", style='Normal.TLabel').pack()
        self.difficulty_label = ttk.Label(difficulty_frame,
                                         text="---",
                                         style='Title.TLabel')
        self.difficulty_label.pack(pady=5)

        return panel

    def _import_item(self, item_number: int):
        """Импорт предмета из текста игры"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Импорт предмета {item_number}")
        dialog.geometry("600x500")
        dialog.configure(bg='#2a2420')

        ttk.Label(dialog,
                 text="Скопируйте предмет из игры (Ctrl+C) и вставьте сюда:",
                 style='Normal.TLabel').pack(pady=10)

        text_area = scrolledtext.ScrolledText(dialog,
                                              width=70,
                                              height=20,
                                              bg='#1a1410',
                                              fg='#d0d0d0',
                                              font=('Courier', 10))
        text_area.pack(padx=10, pady=10)

        def do_import():
            text = text_area.get('1.0', tk.END)
            item = self.parser.parse_item_text(text)

            if item:
                if item_number == 1:
                    self.item1 = item
                    self._update_item_display(1)
                else:
                    self.item2 = item
                    self._update_item_display(2)

                messagebox.showinfo("Успех",
                                   f"Предмет {item_number} успешно импортирован!\n\n"
                                   f"Класс: {item.item_class.value}\n"
                                   f"Префиксов: {item.prefix_count}\n"
                                   f"Суффиксов: {item.suffix_count}")
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось распарсить предмет.\nПроверьте формат текста.")

        ttk.Button(dialog,
                  text="Импортировать",
                  style='Gold.TButton',
                  command=do_import).pack(pady=10)

    def _add_mods_manually(self, item_number: int):
        """Ручное добавление модов"""
        # Упрощенный диалог для добавления модов
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Добавить моды для предмета {item_number}")
        dialog.geometry("500x400")
        dialog.configure(bg='#2a2420')

        ttk.Label(dialog, text="Создание предмета с модами", style='Subtitle.TLabel').pack(pady=10)

        # Класс предмета
        ttk.Label(dialog, text="Класс предмета:", style='Normal.TLabel').pack()
        class_var = tk.StringVar(value="RING")
        class_combo = ttk.Combobox(dialog, textvariable=class_var, state='readonly')
        class_combo['values'] = [ic.value for ic in ItemClass]
        class_combo.pack(pady=5)

        # Список модов
        ttk.Label(dialog, text="Моды (по одному на строку):", style='Normal.TLabel').pack(pady=(10, 0))
        ttk.Label(dialog, text="Формат: P/S Имя_мода Группа [T1/T2/T3] [exclusive] [fractured]",
                 style='Normal.TLabel').pack()

        mods_text = scrolledtext.ScrolledText(dialog, width=60, height=10, bg='#1a1410', fg='#d0d0d0')
        mods_text.pack(padx=10, pady=10)

        mods_text.insert('1.0', "P Life Life T1\nS ColdRes ColdResistance T1\n")

        def create_item():
            try:
                item_class = ItemClass(class_var.get())
                item = Item(item_class=item_class, item_level=86)

                # Парсим моды
                lines = mods_text.get('1.0', tk.END).strip().split('\n')
                for line in lines:
                    if not line.strip():
                        continue

                    parts = line.strip().split()
                    if len(parts) < 3:
                        continue

                    mod_type = ModType.PREFIX if parts[0].upper() == 'P' else ModType.SUFFIX
                    mod_name = parts[1]
                    mod_group = parts[2]
                    tier = ModTier.T1 if 'T1' in parts else (ModTier.T2 if 'T2' in parts else ModTier.T3)
                    is_exclusive = 'exclusive' in [p.lower() for p in parts]
                    is_fractured = 'fractured' in [p.lower() for p in parts]

                    mod = Mod(mod_name, mod_type, tier, mod_group, is_exclusive, is_fractured)
                    item.add_mod(mod)

                if item_number == 1:
                    self.item1 = item
                    self._update_item_display(1)
                else:
                    self.item2 = item
                    self._update_item_display(2)

                messagebox.showinfo("Успех", f"Предмет {item_number} создан с {len(item.mods)} модами")
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка создания предмета:\n{str(e)}")

        ttk.Button(dialog, text="Создать", style='Gold.TButton', command=create_item).pack(pady=10)

    def _update_item_display(self, item_number: int):
        """Обновление отображения предмета"""
        item = self.item1 if item_number == 1 else self.item2
        text_widget = self.item1_info if item_number == 1 else self.item2_info

        text_widget.config(state='normal')
        text_widget.delete('1.0', tk.END)

        if item:
            info = f"{item.item_class.value}\n"
            info += f"Уровень: {item.item_level}\n"
            info += f"Префиксы: {item.prefix_count}/3\n"
            info += f"Суффиксы: {item.suffix_count}/3\n"
            info += f"\nМоды:\n"

            for mod in item.mods:
                prefix = "P" if mod.mod_type == ModType.PREFIX else "S"
                flags = []
                if mod.is_exclusive:
                    flags.append("EX")
                if mod.is_fractured:
                    flags.append("FR")
                flag_str = f" [{'/'.join(flags)}]" if flags else ""
                info += f"{prefix} {mod.name}{flag_str}\n"
        else:
            info = "Предмет не добавлен"

        text_widget.insert('1.0', info)
        text_widget.config(state='disabled')

    def _add_desired_mod(self, mod_type: ModType):
        """Добавление желаемого мода"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Добавить желаемый {'префикс' if mod_type == ModType.PREFIX else 'суффикс'}")
        dialog.geometry("400x300")
        dialog.configure(bg='#2a2420')

        ttk.Label(dialog, text="Название мода:", style='Normal.TLabel').pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)

        ttk.Label(dialog, text="Группа мода:", style='Normal.TLabel').pack(pady=5)
        group_entry = ttk.Entry(dialog, width=40)
        group_entry.pack(pady=5)

        ttk.Label(dialog, text="Тир:", style='Normal.TLabel').pack(pady=5)
        tier_var = tk.StringVar(value="T1")
        tier_combo = ttk.Combobox(dialog, textvariable=tier_var, state='readonly')
        tier_combo['values'] = ['T1', 'T2', 'T3', 'T4', 'T5']
        tier_combo.pack(pady=5)

        exclusive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="Эксклюзивный мод (essence/fossil)", variable=exclusive_var).pack(pady=5)

        def add_mod():
            name = name_entry.get().strip()
            group = group_entry.get().strip()

            if not name or not group:
                messagebox.showwarning("Внимание", "Заполните все поля")
                return

            tier = ModTier[tier_var.get()]
            mod = Mod(name, mod_type, tier, group, is_exclusive=exclusive_var.get())

            if mod_type == ModType.PREFIX:
                self.desired_prefixes.append(mod)
                self.prefix_list.insert(tk.END, f"{name} ({group})")
            else:
                self.desired_suffixes.append(mod)
                self.suffix_list.insert(tk.END, f"{name} ({group})")

            dialog.destroy()

        ttk.Button(dialog, text="Добавить", style='Gold.TButton', command=add_mod).pack(pady=20)

    def _clear_desired_mods(self):
        """Очистка желаемых модов"""
        self.desired_prefixes.clear()
        self.desired_suffixes.clear()
        self.prefix_list.delete(0, tk.END)
        self.suffix_list.delete(0, tk.END)

    def _calculate_basic(self):
        """Базовый расчет рекомбинации"""
        if not self.item1 or not self.item2:
            messagebox.showwarning("Внимание", "Добавьте оба предмета для рекомбинации")
            return

        # Простой расчет вероятностей
        result = self.calculator.calculate_all_outcomes(self.item1, self.item2)

        # Отображение результата
        self.strategy_text.config(state='normal')
        self.strategy_text.delete('1.0', tk.END)

        info = "РЕЗУЛЬТАТЫ РЕКОМБИНАЦИИ:\n\n"
        info += f"Предмет 1: {self.item1.prefix_count}P + {self.item1.suffix_count}S\n"
        info += f"Предмет 2: {self.item2.prefix_count}P + {self.item2.suffix_count}S\n\n"
        info += "Возможные результаты:\n\n"

        for outcome in result['possible_outcomes'][:10]:
            prob = outcome['probability'] * 100
            info += f"{outcome['prefix_count']}P + {outcome['suffix_count']}S: {prob:.1f}%\n"
            for mod in outcome['mods'][:3]:
                info += f"  - {mod.name}\n"
            info += "\n"

        self.strategy_text.insert('1.0', info)
        self.strategy_text.config(state='disabled')

        # Обновление вероятности
        best_prob = result['possible_outcomes'][0]['probability'] if result['possible_outcomes'] else 0
        self._update_probability_display(best_prob)

    def _analyze_craft(self):
        """Анализ желаемого крафта"""
        if not self.desired_prefixes and not self.desired_suffixes:
            messagebox.showwarning("Внимание", "Добавьте хотя бы один желаемый мод")
            return

        # Валидация
        is_valid, issues = self.advisor.validate_desired_combination(
            self.desired_prefixes + self.desired_suffixes
        )

        if not is_valid:
            messagebox.showerror("Невозможная комбинация",
                                "Эта комбинация модов невозможна:\n\n" + "\n".join(issues))
            return

        # Получение рекомендации
        recommendation = self.advisor.analyze_desired_outcome(
            self.desired_prefixes,
            self.desired_suffixes
        )

        # Отображение результатов
        self._display_recommendation(recommendation)

    def _display_recommendation(self, rec):
        """Отображение рекомендации"""
        # Стратегия
        self.strategy_type_label.config(text=rec.strategy.value)

        # Вероятность
        self._update_probability_display(rec.success_probability)
        self.prob_label.config(text=f"{rec.success_probability:.1%}")

        # Попытки
        self.attempts_label.config(text=f"В среднем: {rec.average_attempts}")

        # Сложность
        self.difficulty_label.config(text=rec.feasibility)

        # Цвет сложности
        colors = {
            'Легко': '#00ff00',
            'Средне': '#ffff00',
            'Сложно': '#ff8800',
            'Очень сложно': '#ff0000',
            'Невозможно': '#880000'
        }
        self.difficulty_label.config(foreground=colors.get(rec.feasibility, '#c8aa6e'))

        # Ресурсы
        self.resources_text.config(state='normal')
        self.resources_text.delete('1.0', tk.END)

        res_text = "НЕОБХОДИМЫЕ РЕСУРСЫ:\n\n"
        for resource, amount in rec.estimated_cost.items():
            res_text += f"{resource}:\n  {amount}\n\n"

        res_text += "\nПРЕДУПРЕЖДЕНИЯ:\n\n"
        for warning in rec.warnings:
            res_text += f"• {warning}\n"

        res_text += "\n\nСОВЕТЫ:\n\n"
        for tip in rec.tips:
            res_text += f"• {tip}\n"

        self.resources_text.insert('1.0', res_text)
        self.resources_text.config(state='disabled')

        # План
        self.strategy_text.config(state='normal')
        self.strategy_text.delete('1.0', tk.END)
        self.strategy_text.insert('1.0', '\n'.join(rec.steps))
        self.strategy_text.config(state='disabled')

    def _update_probability_display(self, probability: float):
        """Визуальное отображение вероятности"""
        self.prob_canvas.delete('all')

        width = self.prob_canvas.winfo_width()
        if width <= 1:
            width = 320  # default

        height = 100

        # Фон
        self.prob_canvas.create_rectangle(0, 0, width, height, fill='#1a1410', outline='')

        # Прогресс бар
        bar_width = width - 40
        bar_height = 30
        x_start = 20
        y_start = 35

        # Серый фон бара
        self.prob_canvas.create_rectangle(x_start, y_start,
                                         x_start + bar_width, y_start + bar_height,
                                         fill='#3a3430', outline='#c8aa6e')

        # Заполненная часть
        fill_width = bar_width * probability
        color = '#00ff00' if probability > 0.3 else '#ffff00' if probability > 0.15 else '#ff8800'

        self.prob_canvas.create_rectangle(x_start, y_start,
                                         x_start + fill_width, y_start + bar_height,
                                         fill=color, outline='')

        # Текст вероятности
        self.prob_canvas.create_text(width // 2, y_start + bar_height // 2,
                                     text=f"{probability:.1%}",
                                     fill='#ffffff',
                                     font=('Arial', 12, 'bold'))


def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = CompactRecombinatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
