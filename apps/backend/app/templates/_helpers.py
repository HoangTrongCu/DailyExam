"""Shared helpers for building templates."""

from __future__ import annotations

import random
from typing import Any


def pick(rng: random.Random, options: list[Any]) -> Any:
    """Return a random element from options."""
    return rng.choice(options)


def build_mcq_choices(correct: int | float, distractors: list[int | float], rng: random.Random) -> list[str]:
    """Build a 4-choice MCQ list with a known correct answer.

    Correct must appear exactly once; duplicates in distractors are filtered.
    """
    seen = {correct}
    unique_distractors: list[int | float] = []
    for d in distractors:
        if d not in seen:
            seen.add(d)
            unique_distractors.append(d)
    # Ensure we have 3 distinct distractors; if not, pad with small deltas
    delta = 1
    while len(unique_distractors) < 3:
        candidate = correct + delta
        if candidate not in seen:
            seen.add(candidate)
            unique_distractors.append(candidate)
        delta += 1
    choices = [correct, *unique_distractors[:3]]
    rng.shuffle(choices)
    return [_format(x) for x in choices]


def _format(value: int | float) -> str:
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def correct_letter(choices: list[str], correct: int | float) -> str:
    """Return the letter (A/B/C/D) matching the formatted correct value."""
    target = _format(correct)
    for idx, choice in enumerate(choices):
        if choice == target:
            return "ABCD"[idx]
    raise ValueError(f"Correct answer {correct} not in choices {choices}")
