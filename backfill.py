"""Paint the contribution graph with two random bands.

Last GREEN_HOT_DAYS (default 60 ≈ two months): 20–44 commits/day.
Older filled days: 2–7 commits/day.
"""

from __future__ import annotations

import os
import random
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DAYS = int(os.environ.get("GREEN_DAYS", "365"))
HOT_DAYS = int(os.environ.get("GREEN_HOT_DAYS", "60"))
HOT_MIN = int(os.environ.get("GREEN_HOT_MIN", "20"))
HOT_MAX = int(os.environ.get("GREEN_HOT_MAX", "44"))
REST_MIN = int(os.environ.get("GREEN_REST_MIN", "2"))
REST_MAX = int(os.environ.get("GREEN_REST_MAX", "7"))


def git(*args: str, extra_env: dict[str, str] | None = None, check: bool = True) -> str:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        env=env,
        check=check,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def detect_identity() -> tuple[str, str]:
    name = os.environ.get("GREEN_GITHUB_USER", "").strip()
    email = os.environ.get("GREEN_GITHUB_EMAIL", "").strip()
    if not name:
        name = git("config", "user.name", check=False)
    if not email:
        email = git("config", "user.email", check=False)
    if not name:
        sys.exit(
            "Set GREEN_GITHUB_USER to your GitHub username "
            "(or git config user.name)."
        )
    if not email:
        email = f"{name}@users.noreply.github.com"
    return name, email


def commits_per_day() -> Counter[str]:
    result = git("log", "--pretty=format:%ad", "--date=format:%Y-%m-%d", check=False)
    return Counter(line for line in result.splitlines() if line)


def target_for(ago: int) -> int:
    if ago < HOT_DAYS:
        return random.randint(HOT_MIN, HOT_MAX)
    return random.randint(REST_MIN, REST_MAX)


def main() -> None:
    name, email = detect_identity()
    counts = commits_per_day()
    today = datetime.now(timezone.utc).date()
    head = git("rev-parse", "HEAD")
    branch = git("symbolic-ref", "--short", "HEAD")
    ref = f"refs/heads/{branch}"
    chunks: list[str] = []
    mark = 0
    created = 0
    hot_summary: list[str] = []
    rest_counts: list[int] = []

    print(f"Committing as {name} <{email}>")
    print(
        f"Last {HOT_DAYS} days: {HOT_MIN}-{HOT_MAX}  |  "
        f"older days: {REST_MIN}-{REST_MAX}"
    )

    for ago in range(DAYS - 1, -1, -1):
        day = today - timedelta(days=ago)
        stamp = day.isoformat()
        have = counts[stamp]
        goal = target_for(ago)
        need = max(0, goal - have)
        hour = random.randint(8, 20)
        if ago < HOT_DAYS:
            hot_summary.append(f"  {stamp}: {have + need} (+{need})")
        else:
            rest_counts.append(have + need)
        for extra in range(need):
            mark += 1
            when = datetime(
                day.year,
                day.month,
                day.day,
                hour,
                extra % 60,
                (extra // 60) % 60,
                tzinfo=timezone.utc,
            )
            ts = int(when.timestamp())
            n = have + extra + 1
            parent = head if mark == 1 else f":{mark - 1}"
            chunks.append(
                f"commit {ref}\n"
                f"mark :{mark}\n"
                f"author {name} <{email}> {ts} +0000\n"
                f"committer {name} <{email}> {ts} +0000\n"
                f"data <<MSG\n"
                f"chore: intensity {stamp} #{n}/{goal}\n"
                f"MSG\n"
                f"from {parent}\n"
            )
            created += 1

    print("Last two months:")
    print("\n".join(hot_summary))
    if rest_counts:
        print(
            f"Older days: {len(rest_counts)} days, "
            f"min {min(rest_counts)} max {max(rest_counts)}"
        )

    if not chunks:
        print("Already at target. Nothing to do.")
        return

    subprocess.run(
        ["git", "fast-import", "--quiet", "--date-format=raw"],
        cwd=ROOT,
        input="".join(chunks).encode("utf-8"),
        check=True,
    )
    git("reset", "--hard", ref)
    print(f"Created {created} commits. Push to GitHub default branch: git push")


if __name__ == "__main__":
    main()
