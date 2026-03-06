"""
interface.py - Interfaz gráfica principal con Tkinter
DailyTask - Sistema de Gestión de Tareas
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import Optional, List
import threading

from core.task import Task, Priority, Status, Category
from core.task_service import TaskService


# ── Paleta de colores ─────────────────────────────────────────────────────────
COLORS = {
    "bg":            "#0F0F1A",
    "surface":       "#1A1A2E",
    "surface2":      "#16213E",
    "accent":        "#6C63FF",
    "accent2":       "#FF6584",
    "accent3":       "#43E97B",
    "text":          "#E8E8F0",
    "text_muted":    "#8888AA",
    "border":        "#2A2A4A",
    "card":          "#1E1E35",
    "hover":         "#252540",
    "urgent":        "#FF4757",
    "high":          "#FFA502",
    "medium":        "#6C63FF",
    "low":           "#2ED573",
    "done":          "#2ED573",
    "pending":       "#FFA502",
    "in_progress":   "#6C63FF",
    "overdue":       "#FF4757",
}

PRIORITY_COLORS = {
    Priority.URGENT: COLORS["urgent"],
    Priority.HIGH:   COLORS["high"],
    Priority.MEDIUM: COLORS["medium"],
    Priority.LOW:    COLORS["low"],
}

STATUS_COLORS = {
    Status.DONE:        COLORS["done"],
    Status.PENDING:     COLORS["pending"],
    Status.IN_PROGRESS: COLORS["in_progress"],
}

FONTS = {
    "title":    ("Segoe UI", 22, "bold"),
    "heading":  ("Segoe UI", 14, "bold"),
    "subhead":  ("Segoe UI", 11, "bold"),
    "body":     ("Segoe UI", 10),
    "small":    ("Segoe UI", 9),
    "mono":     ("Consolas", 10),
}


class DailyTaskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.service = TaskService()
        self.service.register_reminder_callback(self._on_reminder)
        self.service.start_reminder_daemon()

        self._build_window()
        self._build_sidebar()
        self._build_main_area()
        self._show_all_tasks()
        self._start_clock()

    # ── Ventana principal ──────────────────────────────────────────────────────

    def _build_window(self):
        self.title("DailyTask — Gestor de Tareas")
        self.geometry("1200x750")
        self.minsize(900, 600)
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
            fieldbackground=COLORS["surface"],
            background=COLORS["surface"],
            foreground=COLORS["text"],
            selectbackground=COLORS["accent"],
            selectforeground=COLORS["text"],
            borderwidth=0,
        )
        style.configure("Vertical.TScrollbar",
            background=COLORS["surface2"],
            troughcolor=COLORS["surface"],
            borderwidth=0,
            arrowcolor=COLORS["text_muted"],
        )

    # ── Sidebar ────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=COLORS["surface"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / título
        logo_frame = tk.Frame(self.sidebar, bg=COLORS["surface"])
        logo_frame.pack(fill="x", padx=20, pady=(28, 10))

        tk.Label(logo_frame, text="✦", font=("Segoe UI", 28), fg=COLORS["accent"],
                bg=COLORS["surface"]).pack(anchor="w")
        tk.Label(logo_frame, text="DailyTask", font=FONTS["title"],
                fg=COLORS["text"], bg=COLORS["surface"]).pack(anchor="w")
        tk.Label(logo_frame, text="Gestor Personal", font=FONTS["small"],
                fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w")

        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=20, pady=16)

        # Reloj
        self.clock_label = tk.Label(self.sidebar, text="", font=FONTS["mono"],
                                fg=COLORS["text_muted"], bg=COLORS["surface"])
        self.clock_label.pack(padx=20, anchor="w")

        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=20, pady=12)

        # Botón nueva tarea
        self._sidebar_btn("＋  Nueva Tarea", self._open_create_dialog,
                        bg=COLORS["accent"], fg="white")

        tk.Label(self.sidebar, text="VISTAS", font=("Segoe UI", 8, "bold"),
                fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w", padx=20, pady=(18, 4))

        # Navegación
        nav_items = [
            ("○  Todas las Tareas",  self._show_all_tasks),
            ("◈  Tareas Diarias",    self._show_daily_tasks),
            ("▷  Pendientes",        self._show_pending),
            ("◉  En Progreso",       self._show_in_progress),
            ("✓  Completadas",       self._show_done),
            ("⚠  Vencidas",         self._show_overdue),
        ]
        for label, cmd in nav_items:
            self._sidebar_btn(label, cmd)

        tk.Label(self.sidebar, text="FILTRAR", font=("Segoe UI", 8, "bold"),
                fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w", padx=20, pady=(18, 4))

        for cat in Category:
            self._sidebar_btn(f"⬡  {cat.value}", lambda c=cat: self._show_by_category(c))

        # Stats al fondo
        self.stats_frame = tk.Frame(self.sidebar, bg=COLORS["surface2"])
        self.stats_frame.pack(side="bottom", fill="x", padx=12, pady=12)
        self._update_stats_widget()

    def _sidebar_btn(self, text, command, bg=None, fg=None):
        b = tk.Button(
            self.sidebar, text=text, command=command,
            font=FONTS["body"], anchor="w",
            bg=bg or COLORS["surface"], fg=fg or COLORS["text"],
            activebackground=COLORS["hover"], activeforeground=COLORS["text"],
            relief="flat", cursor="hand2", padx=20, pady=7,
            bd=0, highlightthickness=0,
        )
        b.pack(fill="x", padx=8 if not bg else 20, pady=1 if not bg else (0, 8))
        if not bg:
            b.bind("<Enter>", lambda e: b.config(bg=COLORS["hover"]))
            b.bind("<Leave>", lambda e: b.config(bg=COLORS["surface"]))

    # ── Área principal ────────────────────────────────────────────────────────

    def _build_main_area(self):
        self.main = tk.Frame(self, bg=COLORS["bg"])
        self.main.pack(side="left", fill="both", expand=True)

        # Header con búsqueda
        header = tk.Frame(self.main, bg=COLORS["surface2"], pady=12)
        header.pack(fill="x")

        self.view_title = tk.Label(header, text="Todas las Tareas", font=FONTS["heading"],
                                fg=COLORS["text"], bg=COLORS["surface2"])
        self.view_title.pack(side="left", padx=24)

        # Barra de búsqueda
        search_container = tk.Frame(header, bg=COLORS["surface"], bd=0, highlightbackground=COLORS["accent"],
                                    highlightthickness=1)
        search_container.pack(side="right", padx=24)

        tk.Label(search_container, text="⌕", font=("Segoe UI", 13), fg=COLORS["text_muted"],
                bg=COLORS["surface"]).pack(side="left", padx=(10, 4))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        search_entry = tk.Entry(search_container, textvariable=self.search_var,
                                font=FONTS["body"], bg=COLORS["surface"], fg=COLORS["text"],
                                insertbackground=COLORS["accent"], relief="flat",
                                width=26, bd=0)
        search_entry.pack(side="left", ipady=8, padx=(0, 10))
        search_entry.insert(0, "Buscar tareas...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, "end")
                        if search_entry.get() == "Buscar tareas..." else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "Buscar tareas...")
                        if not search_entry.get() else None)

        # Canvas scrollable para las tarjetas
        content = tk.Frame(self.main, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=20, pady=16)

        self.canvas = tk.Canvas(content, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=self.canvas.yview)
        self.task_frame = tk.Frame(self.canvas, bg=COLORS["bg"])

        self.task_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.task_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # ── Renderizado de tareas ─────────────────────────────────────────────────

    def _render_tasks(self, tasks: List[Task], title: str = ""):
        if title:
            self.view_title.config(text=title)

        for w in self.task_frame.winfo_children():
            w.destroy()

        if not tasks:
            empty = tk.Frame(self.task_frame, bg=COLORS["bg"])
            empty.pack(pady=80)
            tk.Label(empty, text="✦", font=("Segoe UI", 48), fg=COLORS["border"],
                    bg=COLORS["bg"]).pack()
            tk.Label(empty, text="Sin tareas aquí", font=FONTS["heading"],
                    fg=COLORS["text_muted"], bg=COLORS["bg"]).pack()
            tk.Label(empty, text="Crea una nueva tarea con el botón del menú",
                    font=FONTS["body"], fg=COLORS["text_muted"], bg=COLORS["bg"]).pack(pady=4)
            return

        for task in tasks:
            self._build_task_card(task)

    def _build_task_card(self, task: Task):
        priority_color = PRIORITY_COLORS[task.priority]
        status_color = STATUS_COLORS[task.status]
        is_overdue = task.is_overdue()

        card = tk.Frame(self.task_frame, bg=COLORS["card"], bd=0,
                        highlightbackground=COLORS["overdue"] if is_overdue else COLORS["border"],
                        highlightthickness=1)
        card.pack(fill="x", pady=5, ipady=2)

        # Banda de color izquierda (prioridad)
        band = tk.Frame(card, bg=priority_color, width=4)
        band.pack(side="left", fill="y")

        inner = tk.Frame(card, bg=COLORS["card"], padx=16, pady=12)
        inner.pack(side="left", fill="both", expand=True)

        # Fila 1: nombre + badges
        row1 = tk.Frame(inner, bg=COLORS["card"])
        row1.pack(fill="x")

        name_color = COLORS["text_muted"] if task.status == Status.DONE else COLORS["text"]
        tk.Label(row1, text=task.name, font=FONTS["subhead"],
                fg=name_color, bg=COLORS["card"]).pack(side="left")

        # Badge categoría
        self._badge(row1, task.category.value, COLORS["surface2"])
        # Badge prioridad
        self._badge(row1, task.priority.value, priority_color)
        # Badge estado
        self._badge(row1, task.status.value, status_color)

        if task.is_daily:
            self._badge(row1, "Diaria", COLORS["accent"])
        if is_overdue:
            self._badge(row1, "VENCIDA", COLORS["overdue"])

        # Fila 2: descripción
        if task.description:
            tk.Label(inner, text=task.description, font=FONTS["small"],
                    fg=COLORS["text_muted"], bg=COLORS["card"],
                    wraplength=600, justify="left").pack(anchor="w", pady=(4, 0))

        # Fila 3: fechas
        row3 = tk.Frame(inner, bg=COLORS["card"])
        row3.pack(fill="x", pady=(8, 0))

        tk.Label(row3, text=f"Creada: {task.created_at.strftime('%d/%m/%Y %H:%M')}",
                font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["card"]).pack(side="left", padx=(0, 16))

        if task.due_date:
            color = COLORS["overdue"] if is_overdue else COLORS["text_muted"]
            tk.Label(row3, text=f"Vence: {task.due_date.strftime('%d/%m/%Y %H:%M')}",
                    font=FONTS["small"], fg=color, bg=COLORS["card"]).pack(side="left", padx=(0, 16))

        if task.reminder:
            tk.Label(row3, text=f"⏰ {task.reminder.strftime('%d/%m/%Y %H:%M')}",
                    font=FONTS["small"], fg=COLORS["accent2"], bg=COLORS["card"]).pack(side="left")

        # Acciones
        actions = tk.Frame(card, bg=COLORS["card"], padx=12)
        actions.pack(side="right", fill="y")

        if task.status != Status.DONE:
            self._action_btn(actions, "✓", COLORS["done"],
                            lambda t=task: self._quick_done(t.id))
            self._action_btn(actions, "▷", COLORS["in_progress"],
                            lambda t=task: self._quick_progress(t.id))
        else:
            self._action_btn(actions, "↺", COLORS["pending"],
                            lambda t=task: self._quick_pending(t.id))

        self._action_btn(actions, "✎", COLORS["accent"],
                        lambda t=task: self._open_edit_dialog(t))
        self._action_btn(actions, "✕", COLORS["accent2"],
                        lambda t=task: self._delete_task(t.id))

    def _badge(self, parent, text, color):
        tk.Label(parent, text=f" {text} ", font=("Segoe UI", 8, "bold"),
                fg="white", bg=color, relief="flat", padx=4, pady=2).pack(side="left", padx=3)

    def _action_btn(self, parent, text, color, command):
        b = tk.Button(parent, text=text, font=("Segoe UI", 12), fg=color,
                    bg=COLORS["card"], activebackground=COLORS["hover"],
                    activeforeground=color, relief="flat", cursor="hand2",
                    command=command, bd=0, width=2)
        b.pack(pady=2)

    # ── Vistas de navegación ──────────────────────────────────────────────────

    def _show_all_tasks(self):
        self._render_tasks(self.service.get_all(), "Todas las Tareas")

    def _show_daily_tasks(self):
        self._render_tasks(self.service.get_daily_tasks(), "Tareas Diarias")

    def _show_pending(self):
        self._render_tasks(self.service.filter_by_status(Status.PENDING), "Pendientes")

    def _show_in_progress(self):
        self._render_tasks(self.service.filter_by_status(Status.IN_PROGRESS), "En Progreso")

    def _show_done(self):
        self._render_tasks(self.service.filter_by_status(Status.DONE), "Completadas")

    def _show_overdue(self):
        self._render_tasks(self.service.get_overdue(), "Tareas Vencidas")

    def _show_by_category(self, category: Category):
        self._render_tasks(self.service.filter_by_category(category), f"Categoría: {category.value}")

    # ── Búsqueda ──────────────────────────────────────────────────────────────

    def _on_search(self, *_):
        query = self.search_var.get().strip()
        if not query or query == "Buscar tareas...":
            self._show_all_tasks()
        else:
            results = self.service.search(query)
            self._render_tasks(results, f'Búsqueda: "{query}"')

    # ── Acciones rápidas ──────────────────────────────────────────────────────

    def _quick_done(self, task_id):
        self.service.mark_done(task_id)
        self._refresh()

    def _quick_progress(self, task_id):
        self.service.mark_in_progress(task_id)
        self._refresh()

    def _quick_pending(self, task_id):
        self.service.mark_pending(task_id)
        self._refresh()

    def _delete_task(self, task_id):
        if messagebox.askyesno("Eliminar tarea",
                            "¿Estás seguro de que deseas eliminar esta tarea?",
                            icon="warning"):
            self.service.delete_task(task_id)
            self._refresh()

    def _refresh(self):
        self._update_stats_widget()
        self._show_all_tasks()

    # ── Diálogo: Crear tarea ──────────────────────────────────────────────────

    def _open_create_dialog(self):
        self._open_task_dialog()

    def _open_edit_dialog(self, task: Task):
        self._open_task_dialog(task)

    def _open_task_dialog(self, task: Optional[Task] = None):
        dlg = tk.Toplevel(self)
        dlg.title("Nueva Tarea" if not task else "Editar Tarea")
        dlg.geometry("520x620")
        dlg.configure(bg=COLORS["bg"])
        dlg.resizable(False, False)
        dlg.grab_set()

        is_edit = task is not None

        def label(parent, text):
            tk.Label(parent, text=text, font=FONTS["small"],
                    fg=COLORS["text_muted"], bg=COLORS["bg"]).pack(anchor="w", pady=(10, 2))

        def entry_field(parent, default=""):
            e = tk.Entry(parent, font=FONTS["body"], bg=COLORS["surface"],
                        fg=COLORS["text"], insertbackground=COLORS["accent"],
                        relief="flat", bd=0, highlightthickness=1,
                        highlightbackground=COLORS["border"],
                        highlightcolor=COLORS["accent"])
            e.pack(fill="x", ipady=8, padx=2)
            if default:
                e.insert(0, default)
            return e

        def combo(parent, values, default=None):
            var = tk.StringVar(value=default or values[0])
            c = ttk.Combobox(parent, textvariable=var, values=values,
                            state="readonly", font=FONTS["body"])
            c.pack(fill="x", pady=2, ipady=6)
            return var

        body = tk.Frame(dlg, bg=COLORS["bg"], padx=28, pady=20)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Nueva Tarea" if not is_edit else "Editar Tarea",
                font=FONTS["heading"], fg=COLORS["text"], bg=COLORS["bg"]).pack(anchor="w", pady=(0, 4))
        tk.Frame(body, bg=COLORS["accent"], height=2).pack(fill="x", pady=(0, 12))

        label(body, "Nombre de la tarea *")
        name_entry = entry_field(body, task.name if is_edit else "")

        label(body, "Descripción")
        desc_entry = entry_field(body, task.description if is_edit else "")

        row_mid = tk.Frame(body, bg=COLORS["bg"])
        row_mid.pack(fill="x")
        col1 = tk.Frame(row_mid, bg=COLORS["bg"])
        col1.pack(side="left", fill="x", expand=True, padx=(0, 8))
        col2 = tk.Frame(row_mid, bg=COLORS["bg"])
        col2.pack(side="left", fill="x", expand=True)

        label(col1, "Prioridad")
        priority_var = combo(col1, [p.value for p in Priority],
                            task.priority.value if is_edit else Priority.MEDIUM.value)

        label(col2, "Categoría")
        category_var = combo(col2, [c.value for c in Category],
                            task.category.value if is_edit else Category.PERSONAL.value)

        label(body, "Fecha límite  (DD/MM/AAAA HH:MM)")
        due_entry = entry_field(body, task.due_date.strftime("%d/%m/%Y %H:%M")
                                if is_edit and task.due_date else "")

        label(body, "Recordatorio  (DD/MM/AAAA HH:MM)  ⏰")
        rem_entry = entry_field(body, task.reminder.strftime("%d/%m/%Y %H:%M")
                                if is_edit and task.reminder else "")

        daily_var = tk.BooleanVar(value=task.is_daily if is_edit else False)
        tk.Checkbutton(body, text="Tarea diaria (se repite cada día)",
                    variable=daily_var, font=FONTS["body"],
                    bg=COLORS["bg"], fg=COLORS["text"],
                    selectcolor=COLORS["surface"], activebackground=COLORS["bg"],
                    activeforeground=COLORS["text"]).pack(anchor="w", pady=(12, 0))

        error_label = tk.Label(body, text="", font=FONTS["small"],
                            fg=COLORS["overdue"], bg=COLORS["bg"])
        error_label.pack(anchor="w")

        def parse_date(s):
            s = s.strip()
            if not s:
                return None
            for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y"):
                try:
                    return datetime.strptime(s, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Formato inválido: '{s}'")

        def save():
            name = name_entry.get().strip()
            if not name:
                error_label.config(text="⚠ El nombre es obligatorio.")
                return

            try:
                due = parse_date(due_entry.get())
                rem = parse_date(rem_entry.get())
            except ValueError as e:
                error_label.config(text=f"⚠ {e}")
                return

            priority = next(p for p in Priority if p.value == priority_var.get())
            category = next(c for c in Category if c.value == category_var.get())

            if is_edit:
                self.service.update_task(
                    task.id,
                    name=name,
                    description=desc_entry.get().strip(),
                    priority=priority,
                    category=category,
                    due_date=due,
                    reminder=rem,
                    is_daily=daily_var.get(),
                )
            else:
                self.service.create_task(
                    name=name,
                    description=desc_entry.get().strip(),
                    priority=priority,
                    category=category,
                    due_date=due,
                    reminder=rem,
                    is_daily=daily_var.get(),
                )

            dlg.destroy()
            self._refresh()

        btn_row = tk.Frame(body, bg=COLORS["bg"])
        btn_row.pack(fill="x", pady=(16, 0))

        tk.Button(btn_row, text="Cancelar", font=FONTS["body"],
                bg=COLORS["surface"], fg=COLORS["text_muted"],
                activebackground=COLORS["hover"], relief="flat",
                cursor="hand2", command=dlg.destroy, padx=20, pady=8).pack(side="left")

        tk.Button(btn_row, text="Guardar Tarea", font=FONTS["subhead"],
                bg=COLORS["accent"], fg="white",
                activebackground="#5A52D5", relief="flat",
                cursor="hand2", command=save, padx=20, pady=8).pack(side="right")

    # ── Stats sidebar ──────────────────────────────────────────────────────────

    def _update_stats_widget(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        stats = self.service.get_stats()

        tk.Label(self.stats_frame, text="RESUMEN", font=("Segoe UI", 8, "bold"),
                fg=COLORS["text_muted"], bg=COLORS["surface2"]).pack(anchor="w", padx=12, pady=(10, 4))

        pairs = [
            ("Total",       stats["total"],       COLORS["text"]),
            ("Pendientes",  stats["pending"],      COLORS["pending"]),
            ("En progreso", stats["in_progress"],  COLORS["in_progress"]),
            ("Completadas", stats["done"],         COLORS["done"]),
            ("Vencidas",    stats["overdue"],      COLORS["overdue"]),
        ]
        for label, val, color in pairs:
            row = tk.Frame(self.stats_frame, bg=COLORS["surface2"])
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=label, font=FONTS["small"],
                    fg=COLORS["text_muted"], bg=COLORS["surface2"]).pack(side="left")
            tk.Label(row, text=str(val), font=("Segoe UI", 10, "bold"),
                    fg=color, bg=COLORS["surface2"]).pack(side="right")

        tk.Frame(self.stats_frame, bg=COLORS["surface2"], height=8).pack()

    # ── Reloj ────────────────────────────────────────────────────────────────

    def _start_clock(self):
        def tick():
            now = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
            self.clock_label.config(text=now)
            self.after(1000, tick)
        tick()

    # ── Recordatorio ─────────────────────────────────────────────────────────

    def _on_reminder(self, task: Task):
        self.after(0, lambda: messagebox.showinfo(
            "⏰ Recordatorio — DailyTask",
            f"Tienes una tarea pendiente:\n\n"
            f"  {task.name}\n\n"
            f"Categoría: {task.category.value}  |  Prioridad: {task.priority.value}",
        ))
