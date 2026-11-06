"""Generate add-on release metadata from Renovate's PR update table."""

import argparse
import json
from pathlib import Path
import re
import subprocess


VERSION = re.compile(
    r"^(version:[ \t]*)([\"']?)(\d+\.\d+\.\d+)\2([ \t]*(?:#.*)?)$", re.MULTILINE
)


def git(*args):
    return subprocess.check_output(["git", *args], text=True)


def version(config):
    match = VERSION.search(config)
    if not match:
        raise ValueError("Expected a top-level semantic version in config.yaml")
    return match.group(3)


def dependency_entries(body):
    columns = None
    entries = []
    for line in body.splitlines():
        if not line.strip().startswith("|"):
            if columns is not None:
                break
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if columns is None:
            if {"Package", "Update", "Change"} <= set(cells):
                columns = cells
            continue
        if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        if len(cells) != len(columns):
            raise ValueError("Malformed Renovate update table row")
        row = dict(zip(columns, cells))
        linked_name = re.match(r"\[([^\]]+)\]\([^)]+\)", row["Package"])
        name = linked_name[1] if linked_name else row["Package"].strip("`")
        change = re.fullmatch(r"`([^`]*)`\s*→\s*`([^`]+)`", row["Change"])
        if not name or not change:
            raise ValueError("Expected a package name and old → new values in Renovate's table")
        entries.append(f"Update `{name}` from {change[1] or 'unpinned'} to {change[2]}")
    if not entries:
        raise ValueError("Renovate update table is missing or empty")
    return entries


def changed_addons(base):
    paths = git("diff", "--name-only", "-z", f"{base}...HEAD").split("\0")
    return sorted(
        {path.split("/")[0] for path in paths if "/" in path}
        & {path.parent.name for path in Path(".").glob("*/config.yaml")}
    )


def release_files(base, title, number, body):
    # Renovate recreates its branch, dropping ignored bot commits. Deriving the
    # output from the base also makes retries safe if those commits are present.
    updates = {}
    addons = changed_addons(base)
    if len(addons) > 1:
        raise ValueError("Expected one add-on per Renovate PR; split this update by add-on")
    for addon in addons:
        config_path = f"{addon}/config.yaml"
        config = Path(config_path).read_text()
        base_version = version(git("show", f"{base}:{config_path}"))
        major, minor, patch = map(int, base_version.split("."))
        if re.match(r"\s*feat(?:\([^)]+\))?:", title, re.IGNORECASE):
            minor, patch = minor + 1, 0
        else:
            patch += 1
        next_version = f"{major}.{minor}.{patch}"
        if version(config) not in (base_version, next_version):
            raise ValueError(f"{addon}: version was changed manually; refusing to overwrite it")
        updates[config_path] = VERSION.sub(
            lambda m: f"{m[1]}{m[2]}{next_version}{m[2]}{m[4]}", config, count=1
        )

        entries = dependency_entries(body)
        changelog_path = f"{addon}/CHANGELOG.md"
        history = git("show", f"{base}:{changelog_path}")
        bullets = "\n".join(f"- {entry} (#{number})" for entry in entries)
        updates[changelog_path] = f"# {next_version}\n\n{bullets}\n\n{history}"
    return updates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr-file", type=Path, required=True, help="GitHub pull request API JSON")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    pr = json.loads(args.pr_file.read_text())
    if git("rev-parse", "HEAD").strip() != pr["head"]["sha"]:
        raise ValueError("PR head changed; refusing to use metadata for a different commit")
    updates = release_files(pr["base"]["sha"], pr["title"], pr["number"], pr["body"] or "")
    changed = [path for path, content in updates.items() if Path(path).read_text() != content]
    for path in changed:
        if args.check:
            print(f"Release metadata needs updating: {path}")
        else:
            Path(path).write_text(updates[path])
            print(f"Updated {path}")
    return int(args.check and bool(changed))


if __name__ == "__main__":
    raise SystemExit(main())
