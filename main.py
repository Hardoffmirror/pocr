#!/usr/bin/env python3
"""
PoE Recombinator Simulator - Главный файл запуска

Симулятор рекомбинаторов Path of Exile с графическим интерфейсом
для расчета вероятностей и симуляции крафта.
"""

import sys
import tkinter as tk
from gui import RecombinatorGUI


def main():
    """Точка входа в приложение"""
    try:
        # Создаем главное окно
        root = tk.Tk()

        # Инициализируем GUI
        app = RecombinatorGUI(root)

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
