# LibreEcho-Docs — Agent instructions

This repository is the public LibreEcho static GitHub Pages site. Keep changes
limited to this site and its documentation, artwork, tests, and Pages workflow.
Read `README.md` before non-trivial work.

## Operating contract

- Complete the user's requested outcome within its intended scope. A fix or
  implementation request authorizes reversible local preparation, an isolated
  purpose-named branch/worktree, necessary in-scope edits, local commits, and appropriate
  validation. A review, diagnosis, explanation, or plan does not authorize
  project edits.
- Ask only for a material decision, genuine scope expansion, or a separately
  gated action. Preserve separate authorization for pushing, pull requests,
  merging, publication, releases, and hardware changes.
- Subject to higher-priority system/developer instructions and these project
  safety boundaries, the user's current request takes precedence over
  procedural skill defaults. If an instruction blocks the requested outcome,
  identify its file, quote the exact blocking text, explain the conflict, and
  finish independent authorized work instead of silently abandoning it.
- Delegate independent bounded research, review, or test analysis only when it
  improves the result. Give each worker disjoint write ownership and verify its
  findings before reporting success.
- Use concise plain language. Report the result, exact evidence, and remaining
  blockers; distinguish local commits, remote publication, CI, and deployment.

## Repository workflow

- `main` is the public production branch. Start work from the fetched current
  `main` in a purpose-named branch such as `docs/<purpose>`; do not commit
  directly to `main` or assume that a local branch is current.
- Before editing, verify repository root, branch, `HEAD`, upstream/default-branch
  relation, worktree registration, and porcelain status. Preserve unrelated
  changes; do not reset, stash, clean, or repurpose another worktree.
- Keep edits within the requested outcome. Necessary cross-repository changes
  belong in separate owning-repository branches; do not perform unrelated
  changes or edit generated output, private evidence or deployed worktrees.
- Never publish device identifiers, serials, MAC addresses, private addresses,
  private manifests, credentials, tokens, or local absolute paths. Keep project
  status language consistent with `README.md` and do not turn unsupported or
  unverified hardware behavior into a public claim.

## Validation

Run the smallest meaningful checks that establish all requested acceptance
criteria, plus all applicable required checks. Broaden or repeat testing only
when changes, failures or unresolved risks justify it. Do not add tests that
merely mirror reversible low-impact implementation details. Bounded background
checks and temporary local test servers are permitted when needed for authorized
validation; stop temporary processes afterward. Report unrelated failures
without fixing them silently or treating incomplete evidence as success.

Use bounded commands and stop when the requested acceptance criteria are
evidenced. The repository's deterministic contract check is:

```bash
python3 tests/site-check.py
```

Run it for every site-content or site-workflow change. If privacy patterns or
the contract test are changed, also run the existing regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_site_check.py'
```

Use the documented local preview only when needed:

```bash
python3 -m http.server 8000
```

The Pages workflow also checks out `aslater3/LibreEcho-UI`, optionally renders
screenshots with its build and Playwright steps, and deploys the resulting Pages
artifact. Do not claim that external workflow, CI, screenshot, or deployment
evidence from a local check. Run `git diff --check` before committing.

## Completion and publication gates

Record the exact commit tested and the exact commands/results. A local commit is
not a push, pull request, merge, Pages publication, or hardware validation.
Those actions require explicit authorization and the appropriate current-branch,
review, CI, and release gates. When a PR/push workflow is authorized, complete its required CI checks without
asking again for each read-only check. Use bounded waits; report pending checks
at the deadline rather than waiting indefinitely.
