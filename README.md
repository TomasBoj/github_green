# github_green

Keeps a green square on your GitHub contribution graph every day.

This is **cosmetic**. GitHub only counts commits, not real work. A scheduled
GitHub Action appends a timestamp to `.green/activity.log`, commits, and
pushes. That commit is what turns the day green.

## Setup (required — the bot does not run until the repo is on GitHub)

1. Create a **private** repository on GitHub named `github_green` (or any name).
2. Push this folder to that repository’s **default branch** (`main` or `master`).
3. Open the repo → **Actions** → allow workflows if GitHub asks.
4. **Actions** → **Keep GitHub green** → **Run workflow** (first run is manual;
   the daily schedule starts after that).
5. GitHub profile → **Settings** → **Contributions & activity** → enable
   **Include private contributions**.

The square can take a few minutes (sometimes up to a day) to appear.

## Fill the past year (optional)

Daily Action only greens **today and future days**. To fill history:

```bash
python backfill.py
git push
```

Set your GitHub username first if it is not detected:

```bash
set GREEN_GITHUB_USER=your-username
python backfill.py
```

Use the same email GitHub shows in
**Settings → Emails** (`id+username@users.noreply.github.com`).
The script prints the email it will use; override with `GREEN_GITHUB_EMAIL`
if needed.
