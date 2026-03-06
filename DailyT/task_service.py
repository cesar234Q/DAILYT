"""
task_service.py - Lógica de negocio para gestión de tareas
DailyTask - Sistema de Gestión de Tareas
"""

import json
import os
import threading
from datetime import datetime
from typing import Callable, List, Optional

from core.task import Category, Priority, Status, Task


DATA_FILE = "data/tasks.json"


class TaskService:
    def __init__(self):
        self._tasks: List[Task] = []
        self._reminder_callbacks: List[Callable] = []
        self._reminder_thread: Optional[threading.Thread] = None
        self._running = False
        self._ensure_data_dir()
        self.load_tasks()

    # ── Storage ──────────────────────────────────────────────────────────────

    def _ensure_data_dir(self):
        os.makedirs("data", exist_ok=True)

    def save_tasks(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self._tasks], f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._tasks = [Task.from_dict(d) for d in data]
            except (json.JSONDecodeError, KeyError):
                self._tasks = []
        else:
            self._tasks = []

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def create_task(
        self,
        name: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        category: Category = Category.PERSONAL,
        due_date: Optional[datetime] = None,
        reminder: Optional[datetime] = None,
        is_daily: bool = False,
    ) -> Task:
        task = Task(
            name=name.strip(),
            description=description.strip(),
            priority=priority,
            category=category,
            due_date=due_date,
            reminder=reminder,
            is_daily=is_daily,
        )
        self._tasks.append(task)
        self.save_tasks()
        return task

    def delete_task(self, task_id: str) -> bool:
        before = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        if len(self._tasks) < before:
            self.save_tasks()
            return True
        return False

    def mark_done(self, task_id: str) -> bool:
        task = self.get_by_id(task_id)
        if task:
            task.mark_done()
            self.save_tasks()
            return True
        return False

    def mark_pending(self, task_id: str) -> bool:
        task = self.get_by_id(task_id)
        if task:
            task.mark_pending()
            self.save_tasks()
            return True
        return False

    def mark_in_progress(self, task_id: str) -> bool:
        task = self.get_by_id(task_id)
        if task:
            task.mark_in_progress()
            self.save_tasks()
            return True
        return False

    def update_task(self, task_id: str, **kwargs) -> bool:
        task = self.get_by_id(task_id)
        if not task:
            return False
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        self.save_tasks()
        return True

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_all(self) -> List[Task]:
        return list(self._tasks)

    def get_by_id(self, task_id: str) -> Optional[Task]:
        return next((t for t in self._tasks if t.id == task_id), None)

    def search(self, query: str) -> List[Task]:
        q = query.lower()
        return [
            t for t in self._tasks
            if q in t.name.lower() or q in t.description.lower()
        ]

    def filter_by_status(self, status: Status) -> List[Task]:
        return [t for t in self._tasks if t.status == status]

    def filter_by_priority(self, priority: Priority) -> List[Task]:
        return [t for t in self._tasks if t.priority == priority]

    def filter_by_category(self, category: Category) -> List[Task]:
        return [t for t in self._tasks if t.category == category]

    def get_daily_tasks(self) -> List[Task]:
        return [t for t in self._tasks if t.is_daily]

    def get_overdue(self) -> List[Task]:
        return [t for t in self._tasks if t.is_overdue()]

    def get_stats(self) -> dict:
        total = len(self._tasks)
        done = len([t for t in self._tasks if t.status == Status.DONE])
        pending = len([t for t in self._tasks if t.status == Status.PENDING])
        in_progress = len([t for t in self._tasks if t.status == Status.IN_PROGRESS])
        overdue = len(self.get_overdue())
        return {
            "total": total,
            "done": done,
            "pending": pending,
            "in_progress": in_progress,
            "overdue": overdue,
        }

    # ── Reminders ─────────────────────────────────────────────────────────────

    def register_reminder_callback(self, callback: Callable):
        self._reminder_callbacks.append(callback)

    def start_reminder_daemon(self):
        self._running = True
        self._reminder_thread = threading.Thread(
            target=self._reminder_loop, daemon=True
        )
        self._reminder_thread.start()

    def stop_reminder_daemon(self):
        self._running = False

    def _reminder_loop(self):
        import time
        notified = set()
        while self._running:
            now = datetime.now()
            for task in self._tasks:
                if (
                    task.reminder
                    and task.id not in notified
                    and task.status != Status.DONE
                    and abs((now - task.reminder).total_seconds()) < 60
                ):
                    notified.add(task.id)
                    for cb in self._reminder_callbacks:
                        try:
                            cb(task)
                        except Exception:
                            pass
            time.sleep(30)
