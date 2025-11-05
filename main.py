#!/usr/bin/env python3
"""
PoE Recombinator Simulator - Главный файл запуска

Симулятор рекомбинаторов Path of Exile с графическим интерфейсом
для расчета вероятностей и симуляции крафта.
"""

import sys
import tkinter as tk


def main():
    """Точка входа в приложение"""
    try:
        # Проверяем аргументы командной строки
        use_old_gui = '--old' in sys.argv or '--tabs' in sys.argv

        # Создаем главное окно
        root = tk.Tk()

        # Выбираем GUI
        if use_old_gui:
            from gui import RecombinatorGUI
            app = RecombinatorGUI(root)
            print("Запущен старый интерфейс с вкладками")
        else:
            from gui_new import CompactRecombinatorGUI
            app = CompactRecombinatorGUI(root)
            print("Запущен новый компактный интерфейс")

        # Запускаем главный цикл
        root.mainloop()

    except Exception as e:
        print(f"Ошибка запуска приложения: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
