"""Select affected add-ons; publish only add-ons whose version changed."""

import argparse
import json
from pathlib import Path

from release import git, version


def build_matrix(base, event):
    changed = git("diff", "--no-renames", "--name-only", "-z", base, "HEAD").split("\0")
    rebuild_all = any(
        path in changed
        for path in (
            ".github/workflows/builder.yaml",
            ".github/workflows/build-app.yaml",
            ".github/scripts/build_matrix.py",
            ".github/scripts/release.py",
        )
    )
    matrix = []
    for config in sorted(Path(".").glob("*/config.yaml")):
        addon = config.parent.name
        monitored = (
            f"{addon}/config.yaml",
            f"{addon}/Dockerfile",
            f"{addon}/build.yaml",
            f"{addon}/.dockerignore",
            f"{addon}/Dockerfile.dockerignore",
        )
        if not rebuild_all and not any(
            path in monitored or path.startswith(f"{addon}/rootfs/") for path in changed
        ):
            continue
        publish = False
        if event == "push":
            exists = git("ls-tree", "--name-only", base, "--", str(config)).strip()
            publish = not exists or version(config.read_text()) != version(
                git("show", f"{base}:{config}")
            )
        matrix.append({"app": addon, "publish": publish})
    return matrix


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--event", choices=("push", "pull_request"), required=True)
    args = parser.parse_args()
    print(json.dumps(build_matrix(args.base, args.event)))
