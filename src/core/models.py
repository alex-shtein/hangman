from dataclasses import dataclass

DIFFICULTIES = ["Лёгкая", "Средняя", "Сложная", "Случайная"]


@dataclass
class Settings:
    difficulty: str = DIFFICULTIES[0]
    category: str = ""


@dataclass
class Stats:
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    best_streak: int = 0
    current_streak: int = 0
