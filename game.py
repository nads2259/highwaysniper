#!/usr/bin/env python3
"""Highway Sniper — a tiny terminal target-practice game."""

from __future__ import annotations

import random
import sys
import time


LANE_COUNT = 5
ROUNDS = 8
WINDOW_SECONDS = 2.0
LANE_LABELS = "ABCDE"


def draw_highway(target_lane: int) -> str:
    rows = []
    for i in range(LANE_COUNT):
        marker = ">>> TARGET <<<" if i == target_lane else ""
        rows.append(f"  {LANE_LABELS[i]} |========={marker:^14}=========|")
    return "\n".join(rows)


def play() -> int:
    score = 0
    print("Highway Sniper")
    print("Type the lane letter (A–E) before the target drives out of range.\n")

    for round_no in range(1, ROUNDS + 1):
        target = random.randrange(LANE_COUNT)
        print(f"Round {round_no}/{ROUNDS}")
        print(draw_highway(target))
        print("Lane? ", end="", flush=True)

        start = time.monotonic()
        guess = sys.stdin.readline().strip().upper()
        elapsed = time.monotonic() - start

        if elapsed > WINDOW_SECONDS:
            print(f"Too slow ({elapsed:.1f}s). Target escaped.\n")
            continue
        if guess == LANE_LABELS[target]:
            score += 1
            print("Hit!\n")
        else:
            print(f"Miss. It was lane {LANE_LABELS[target]}.\n")

    print(f"Final score: {score}/{ROUNDS}")
    return score


def main() -> None:
    play()


if __name__ == "__main__":
    main()
