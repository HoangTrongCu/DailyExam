"""Shared helpers for template modules."""

import random


def pick(rng: random.Random, options: list):
    return rng.choice(options)


def format_number(v) -> str:
    if isinstance(v, int) or (isinstance(v, float) and float(v).is_integer()):
        return str(int(v))
    return f"{v:.2f}".rstrip("0").rstrip(".")


def build_mcq_choices(correct, distractors: list, rng: random.Random) -> list[str]:
    seen = {correct}
    unique: list = []
    for d in distractors:
        if d not in seen:
            seen.add(d)
            unique.append(d)
    delta = 1
    while len(unique) < 3:
        cand = correct + delta
        if cand not in seen:
            seen.add(cand)
            unique.append(cand)
        delta += 1
    choices = [correct, *unique[:3]]
    rng.shuffle(choices)
    return [format_number(c) for c in choices]


def correct_letter(choices: list[str], correct) -> str:
    target = format_number(correct)
    for idx, choice in enumerate(choices):
        if choice == target:
            return "ABCD"[idx]
    raise ValueError(f"{correct} not in {choices}")
