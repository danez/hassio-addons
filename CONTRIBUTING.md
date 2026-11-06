# Updates and releases

Renovate maintains one dependency update PR per add-on. Each group includes its
Docker images, pinned APK packages, and annotated `_VERSION` dependencies.
New update branches are created during 00:00–06:00 Europe/Berlin; existing PRs can
still be refreshed outside that window. This batches available updates, but does
not guarantee exactly one release each day.

Minor, patch, pin, and digest updates can merge automatically after CI succeeds.
If any dependency in a group has a major update, the entire PR needs manual
review. Tooling updates are separate PRs and use the same automerge policy.
Renovate performs the merge itself (`platformAutomerge: false`), so eligibility
is reconsidered when an existing batch gains a major update.

## Release metadata

The changelog workflow calls `.github/scripts/release.py`. It reads Renovate's
update table from the PR description, lists each package with its old and new
values, and adds one version section to the add-on's changelog. The table columns
are configured in `renovate.json`; a missing or malformed table fails the check.
Released history comes from the base branch. The pending section is generated;
put handwritten release notes in a separate, manually maintained PR.

Dependency updates get an add-on patch bump. A `feat:` PR gets a minor bump, as
before. A dependency major update requires review but does not automatically
mean the add-on itself has a breaking change. For a deliberate add-on major
release, use a manual PR with the version and release notes you choose.

The changelog bot's email remains in `gitIgnoredAuthors`: Renovate can recreate
the branch and drop the generated bot commit when updates arrive. Generation is
also repeatable when that commit is retained, so the bot's own event produces no
further commit. The workflows read the current description from GitHub instead of
an event snapshot and also run when the description is edited. They reject PR
metadata whose head SHA differs from the checked-out commit. `--check` verifies
the complete output, including on bot commits, so missing or stale release
metadata fails the check. The PR description is the source of package details;
the script does not independently verify them against the Dockerfile.

The builder validates changed add-ons on PRs and pushes. It publishes versioned
images and `latest` only on a push where that add-on's `config.yaml` version
changed. Workflow-only changes validate all add-ons without overwriting released
images. Publication jobs are serialized per add-on, separately from validation.

## GitHub configuration

Keep `CHANGELOG_TOKEN` configured with permission to push to Renovate branches.
It must be a PAT or GitHub App token whose pushes trigger workflows; using the
default `GITHUB_TOKEN` would not trigger the checks for the generated commit.

Require these checks on `main`:

- `Release checks`
- `Build checks`
- `Lint checks`

Require branches to be up to date before merging. If approval rules require a
human review for every PR, give Renovate the appropriate review bypass to allow
non-major updates to merge automatically. Do not bypass the required checks.
These repository settings are managed in GitHub, outside the workflow files.

Existing ungrouped Renovate PRs can be replaced by new grouped PRs after the new
configuration lands; let Renovate reconcile them before merging updates.

## Local verification

No Python packages are required:

```sh
python3 -m unittest discover -s .github/scripts -p 'test_*.py' -v
```

Tests create temporary Git repositories to cover generation, repeated runs,
additional grouped updates, branch recreation, bot events, independent versions,
and the publishing gate. To inspect a dependency PR without changing files:

```sh
gh api repos/danez/hassio-addons/pulls/123 > /tmp/renovate-pr.json
python3 .github/scripts/release.py --pr-file /tmp/renovate-pr.json --check
python3 .github/scripts/build_matrix.py --base origin/main --event pull_request
```

Remove `--check` to write the proposed version and changelog. The scripts expect
to run from the repository root, on the PR head commit. They report the packages
in Renovate's table; this is not an inventory of transitive dependencies or
unversioned APT packages.

Alpine can remove pinned package revisions. Grouping reduces incompatible update
branches, but old commits are not guaranteed to remain buildable. The APK registry
branch in `renovate.json` must match the Alpine release in the base image; check
this when reviewing a major base-image update.
