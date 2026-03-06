# DailyTask 📋

> Sistema de gestión de tareas personal — proyecto académico

---

## Estructura del proyecto

```
DailyTask/
├── main.py                  # Punto de entrada
├── core/
│   ├── __init__.py
│   ├── task.py              # Modelo de datos (Task, Priority, Status, Category)
│   └── task_service.py      # Lógica de negocio y persistencia
├── ui/
│   ├── __init__.py
│   └── interface.py         # Interfaz gráfica (Tkinter)
├── data/
│   └── tasks.json           # Almacenamiento local (generado automáticamente)
└── README.md
```

---

## Requisitos

- Python 3.8 o superior
- Tkinter (incluido por defecto en Python estándar)

---

## Cómo ejecutar

```bash
# Desde la carpeta raíz del proyecto
python main.py
```

---

## Funcionalidades

| Funcionalidad            | Descripción                                          |
|--------------------------|------------------------------------------------------|
| Crear tareas             | Formulario completo con todos los campos             |
| Listar tareas            | Vista de tarjetas con colores por prioridad          |
| Marcar como hecha        | Botón rápido ✓ en cada tarjeta                       |
| Tareas diarias           | Flag especial para tareas recurrentes                |
| Fecha límite             | Plazo de entrega con alerta visual si vence          |
| Búsqueda                 | Barra de búsqueda en tiempo real                     |
| Recordatorio / alarma    | Hilo daemon que dispara notificación emergente       |
| Prioridades              | Baja / Media / Alta / Urgente con colores            |
| Estado                   | Pendiente / En Progreso / Completada                 |
| Categorías               | Personal / Trabajo / Estudio / Salud / Finanzas      |
| Eliminar tareas          | Con confirmación de diálogo                          |
| Editar tareas            | Mismo formulario reutilizado                         |
| Estadísticas             | Panel lateral con resumen numérico                   |
| Persistencia             | JSON local, sin base de datos externa                |

---

## Estándares de código

- PEP 8 — nombres en `snake_case`, clases en `PascalCase`
- Enums para tipos cerrados (`Priority`, `Status`, `Category`)
- Separación de responsabilidades: modelo / servicio / interfaz
- Hilos separados para recordatorios (no bloquean la UI)

---

## Git — flujo de trabajo sugerido

```bash
git init
git add .
git commit -m "feat: estructura inicial de DailyTask"

# Para cada nueva funcionalidad:
git checkout -b feature/nombre-funcionalidad
# ... cambios ...
git commit -m "feat: descripción del cambio"
git checkout main
git merge feature/nombre-funcionalidad
```

---

## Autor

Proyecto académico — Sistemas de Información
