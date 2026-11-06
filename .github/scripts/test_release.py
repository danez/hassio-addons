import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from build_matrix import build_matrix
from release import dependency_entries, git, release_files, version


SCRIPTS = Path(__file__).resolve().parent
BOT_EMAIL = "120286224+danez-bot@users.noreply.github.com"
DOCKERFILE = """FROM ghcr.io/example/base:1.0.0@sha256:aaaaaaaaaaaaaaaa
# renovate: datasource=github-releases depName=restic packageName=restic/restic
ARG RESTIC_VERSION=0.19.0
RUN apk add --no-cache \\
  cifs-utils=7.4-r0 \\
  tzdata=2026e-r0
"""


class DependencyTests(unittest.TestCase):
    def test_rclone_pr_196(self):
        body = """This PR contains the following updates:

| Package | Update | Change |
|---|---|---|
| [rclone](https://redirect.github.com/rclone/rclone) | minor | `1.75.2` → `1.76.0` |

---

### Release Notes
"""
        self.assertEqual(
            dependency_entries(body), ["Update `rclone` from 1.75.2 to 1.76.0"]
        )

    def test_action_digest_pr_195_with_extra_column_and_changelog_link(self):
        body = """This PR contains the following updates:

| Package | Type | Update | Change |
|---|---|---|---|
| [frenck/action-addon-linter](https://redirect.github.com/frenck/action-addon-linter) ([changelog](https://redirect.github.com/frenck/action-addon-linter/compare/b9cfd1b..d516772)) | action | digest | `b9cfd1b` → `d516772` |
"""
        self.assertEqual(
            dependency_entries(body),
            ["Update `frenck/action-addon-linter` from b9cfd1b to d516772"],
        )

    def test_grouped_updates_and_plain_package_names(self):
        body = """| Package | Update | Change |
|---|---|---|
| `cifs-utils` | minor | `7.4-r0` → `7.5-r1` |
| tzdata | patch | `2026e-r0` → `2026f-r0` |
| [ghcr.io/hassio-addons/base](https://example.com/base) | digest | `aaaaaaa` → `bbbbbbb` |

| Package | Update | Change |
|---|---|---|
| ignored-release-note-table | patch | `1` → `2` |
"""
        self.assertEqual(
            dependency_entries(body), [
                "Update `cifs-utils` from 7.4-r0 to 7.5-r1",
                "Update `tzdata` from 2026e-r0 to 2026f-r0",
                "Update `ghcr.io/hassio-addons/base` from aaaaaaa to bbbbbbb",
            ],
        )

    def test_missing_empty_and_malformed_tables_fail(self):
        header = "| Package | Update | Change |\n|---|---|---|\n"
        for body in ("", header, header + "| tool | patch |\n", header + "| tool | patch | unknown |\n"):
            with self.subTest(body=body), self.assertRaises(ValueError):
                dependency_entries(body)

    def test_version_quotes_and_comments(self):
        for line in ('version: "1.2.3" # release', "version: '1.2.3'", "version: 1.2.3"):
            with self.subTest(line=line):
                self.assertEqual(version(line + "\n"), "1.2.3")
        with self.assertRaises(ValueError):
            version("version: latest\n")


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        previous = Path.cwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(temporary.name)
        git("init", "-q", "--initial-branch=main")
        git("config", "user.name", "Test Renovate")
        git("config", "user.email", "renovate@example.test")
        git("config", "commit.gpgsign", "false")
        git("config", "core.hooksPath", "/dev/null")
        for addon, addon_version in (("backup", "1.0.0"), ("other", "3.0.0")):
            Path(addon).mkdir()
            Path(addon, "Dockerfile").write_text(DOCKERFILE)
            Path(addon, "config.yaml").write_text(f'name: {addon}\nversion: "{addon_version}" # keep formatting\n')
            Path(addon, "CHANGELOG.md").write_text(f"# {addon_version}\n\n- Existing release\n")
        self.commit()
        self.base = git("rev-parse", "HEAD").strip()
        self.body = "| Package | Update | Change |\n|---|---|---|\n| cifs-utils | minor | `7.4-r0` → `7.5-r1` |\n"

    def commit(self, author=None):
        git("add", ".")
        args = ["commit", "-qm", "Test update"]
        if author:
            args.extend(["--author", author])
        git(*args)

    def change(self, path="backup/Dockerfile", old="7.4-r0", new="7.5-r1"):
        file = Path(path)
        file.write_text(file.read_text().replace(old, new))
        self.commit()

    def generate(self, title="fix(deps): update backup dependencies"):
        updates = release_files(self.base, title, 42, self.body)
        for path, content in updates.items():
            Path(path).write_text(content)
        return updates

    def cli(self, *extra, title="fix(deps): update backup dependencies", head=None):
        pr = {
            "base": {"sha": self.base},
            "head": {"sha": head or git("rev-parse", "HEAD").strip()},
            "title": title, "number": 42, "body": self.body,
        }
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as file:
            json.dump(pr, file)
            file.flush()
            return subprocess.run(
                [sys.executable, str(SCRIPTS / "release.py"), "--pr-file", file.name, *extra],
                text=True, capture_output=True,
            )

    def test_check_rejects_missing_metadata_without_writing(self):
        self.change()
        before = Path("backup/config.yaml").read_text()
        check = self.cli("--check")
        self.assertEqual(check.returncode, 1, check.stderr)
        self.assertEqual(Path("backup/config.yaml").read_text(), before)
        self.assertEqual(self.cli().returncode, 0)
        self.assertEqual(self.cli("--check").returncode, 0)

    def test_generation_is_idempotent_and_preserves_history_and_format(self):
        history = Path("backup/CHANGELOG.md").read_text()
        self.change()
        updates = self.generate()
        self.assertEqual(updates, self.generate())
        self.assertEqual(Path("backup/config.yaml").read_text(), 'name: backup\nversion: "1.0.1" # keep formatting\n')
        self.assertTrue(updates["backup/CHANGELOG.md"].endswith(history))
        self.assertIn("cifs-utils", updates["backup/CHANGELOG.md"])
        self.assertNotIn("other/config.yaml", updates)

    def test_bot_event_is_idempotent_but_check_still_verifies(self):
        self.change()
        self.generate()
        self.commit(f"Changelog Bot <{BOT_EMAIL}>")
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.cli("--check").returncode, 0)
        Path("backup/CHANGELOG.md").write_text("stale\n")
        self.assertEqual(self.cli("--check").returncode, 1)

    def test_new_update_regenerates_entries_without_another_bump(self):
        self.change()
        self.generate()
        self.commit(f"Changelog Bot <{BOT_EMAIL}>")
        self.change(old="2026e-r0", new="2026f-r0")
        self.body += "| tzdata | patch | `2026e-r0` → `2026f-r0` |\n"
        self.assertEqual(self.cli("--check").returncode, 1)
        self.generate()
        self.assertEqual(version(Path("backup/config.yaml").read_text()), "1.0.1")
        changelog = Path("backup/CHANGELOG.md").read_text()
        self.assertEqual(changelog.count("# 1.0.1\n"), 1)
        self.assertIn("cifs-utils", changelog)
        self.assertIn("tzdata", changelog)
        self.assertEqual(self.cli("--check").returncode, 0)

    def test_renovate_recreation_drops_bot_commit_and_rebuilds_metadata(self):
        self.change()
        update = git("rev-parse", "HEAD").strip()
        self.generate()
        self.commit(f"Changelog Bot <{BOT_EMAIL}>")
        # This repository is temporary; simulate Renovate dropping its bot's commit.
        git("reset", "--hard", update)
        self.change(old="2026e-r0", new="2026f-r0")
        self.body += "| tzdata | patch | `2026e-r0` → `2026f-r0` |\n"
        self.assertEqual(self.cli().returncode, 0)
        self.assertEqual(self.cli("--check").returncode, 0)
        self.assertEqual(version(Path("backup/config.yaml").read_text()), "1.0.1")
        changelog = Path("backup/CHANGELOG.md").read_text()
        self.assertIn("cifs-utils", changelog)
        self.assertIn("tzdata", changelog)

    def test_recreated_branch_uses_new_base_version(self):
        self.change("backup/config.yaml", "1.0.0", "1.0.1")
        Path("backup/CHANGELOG.md").write_text("# 1.0.1\n\n- Another release\n")
        self.commit()
        self.base = git("rev-parse", "HEAD").strip()
        self.change()
        self.generate()
        self.assertEqual(version(Path("backup/config.yaml").read_text()), "1.0.2")
        self.assertIn("- Another release", Path("backup/CHANGELOG.md").read_text())

    def test_manual_version_override_is_not_overwritten(self):
        self.change("backup/config.yaml", "1.0.0", "2.0.0")
        before = Path("backup/config.yaml").read_text()
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertEqual(Path("backup/config.yaml").read_text(), before)

    def test_feature_bump(self):
        self.change()
        self.generate("feat(backup): improve backup support")
        self.assertEqual(version(Path("backup/config.yaml").read_text()), "1.1.0")
        self.assertEqual(version(Path("other/config.yaml").read_text()), "3.0.0")

    def test_addons_have_independent_releases(self):
        self.change()
        self.generate()
        self.commit()
        self.base = git("rev-parse", "HEAD").strip()
        self.change("other/Dockerfile")
        self.generate()
        self.assertEqual(version(Path("backup/config.yaml").read_text()), "1.0.1")
        self.assertEqual(version(Path("other/config.yaml").read_text()), "3.0.1")

    def test_multiple_addons_in_one_pr_fail_instead_of_misattributing_updates(self):
        self.change()
        self.change("other/Dockerfile")
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("one add-on per Renovate PR", result.stderr)

    def test_description_edit_refreshes_changelog_after_bot_commit(self):
        self.change()
        self.generate()
        self.commit(f"Changelog Bot <{BOT_EMAIL}>")
        self.body += "| tzdata | patch | `2026e-r0` → `2026f-r0` |\n"
        self.assertEqual(self.cli("--check").returncode, 1)
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(version(Path("backup/config.yaml").read_text()), "1.0.1")
        self.assertIn("tzdata", Path("backup/CHANGELOG.md").read_text())

    def test_different_pr_head_is_rejected(self):
        self.change()
        result = self.cli(head=self.base)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("different commit", result.stderr)

    def test_tooling_only_change_has_no_release(self):
        Path("renovate.json").write_text("{}\n")
        self.commit()
        self.assertEqual(self.generate(), {})
        self.assertEqual(build_matrix(self.base, "push"), [])

    def test_pr_metadata_is_data_not_shell_code(self):
        self.change()
        self.body = self.body.replace("cifs-utils", "$(touch unexpected)")
        result = self.cli(title="fix: update $(touch unexpected) `touch unexpected`")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(Path("unexpected").exists())
        self.assertIn("$(touch unexpected)", Path("backup/CHANGELOG.md").read_text())

    def test_build_without_bump_does_not_publish(self):
        self.change()
        self.assertEqual(build_matrix(self.base, "push"), [{"app": "backup", "publish": False}])

    def test_bump_publishes_only_on_push(self):
        self.change()
        self.generate()
        self.commit()
        self.assertEqual(build_matrix(self.base, "push"), [{"app": "backup", "publish": True}])
        self.assertEqual(build_matrix(self.base, "pull_request"), [{"app": "backup", "publish": False}])

    def test_rootfs_changes_build_but_documentation_does_not(self):
        Path("backup/rootfs").mkdir()
        Path("backup/rootfs/start.sh").write_text("exit 0\n")
        self.commit()
        self.assertEqual(build_matrix(self.base, "push"), [{"app": "backup", "publish": False}])
        self.base = git("rev-parse", "HEAD").strip()
        Path("backup/README.md").write_text("Documentation\n")
        Path("backup/Dockerfile.notes").write_text("Notes\n")
        self.commit()
        self.assertEqual(build_matrix(self.base, "push"), [])

    def test_workflow_change_validates_all_without_republishing(self):
        Path(".github/workflows").mkdir(parents=True)
        Path(".github/workflows/builder.yaml").write_text("# new builder\n")
        self.commit()
        self.assertEqual(build_matrix(self.base, "push"), [
            {"app": "backup", "publish": False}, {"app": "other", "publish": False},
        ])

    def test_new_addon_is_published(self):
        Path("new").mkdir()
        Path("new/config.yaml").write_text('version: "1.0.0"\n')
        self.commit()
        self.assertEqual(build_matrix(self.base, "push"), [{"app": "new", "publish": True}])


if __name__ == "__main__":
    unittest.main()
