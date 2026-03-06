"""
task.py - Modelo principal de tarea
DailyTask - Sistema de Gestión de Tareas
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class Priority(Enum):
    LOW = "Baja"
    MEDIUM = "Media"
    HIGH = "Alta"
    URGENT = "Urgente"


class Status(Enum):
    PENDING = "Pendiente"
    IN_PROGRESS = "En Progreso"
    DONE = "Completada"


class Category(Enum):
    PERSONAL = "Personal"
    WORK = "Trabajo"
    STUDY = "Estudio"
    HEALTH = "Salud"
    FINANCE = "Finanzas"
    OTHER = "Otra"


@dataclass
class Task:
    name: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    category: Category = Category.PERSONAL
    status: Status = Status.PENDING
    due_date: Optional[datetime] = None
    reminder: Optional[datetime] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    is_daily: bool = False

    def mark_done(self):
        self.status = Status.DONE
        self.completed_at = datetime.now()

    def mark_pending(self):
        self.status = Status.PENDING
        self.completed_at = None

    def mark_in_progress(self):
        self.status = Status.IN_PROGRESS

    def is_overdue(self) -> bool:
        if self.due_date and self.status != Status.DONE:
            return datetime.now() > self.due_date
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "category": self.category.value,
            "status": self.status.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "reminder": self.reminder.isoformat() if self.reminder else None,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_daily": self.is_daily,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        task = cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            priority=Priority(data["priority"]),
            category=Category(data["category"]),
            status=Status(data["status"]),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            reminder=datetime.fromisoformat(data["reminder"]) if data.get("reminder") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            is_daily=data.get("is_daily", False),
        )
        return task
