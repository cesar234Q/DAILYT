"""
main.py - Punto de entrada de DailyTask
DailyTask - Sistema de Gestión de Tareas
"""

import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(__file__))

from ui.interface import DailyTaskApp


def main():
    app = DailyTaskApp()
    app.mainloop()


if __name__ == "__main__":
    main()
