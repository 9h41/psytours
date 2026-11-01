---
name: psy-tours-publish
description: Prepare and publish an approved Psy-Tours release from preview to main through a pull request, while preserving the preview branch.
---

# Publish Psy-Tours

Follow the repository's `AGENTS.md` and speak plain French with the editor. This skill prepares a production release when explicitly requested; creating the skill does not authorize a release. Keep the `preview` branch and its deployment intact throughout, including after merging. Never use `--delete-branch` or any cleanup that deletes or resets `preview`.

## Before preparing a release

1. Inspect the current checkout and remote state, and preserve unrelated uncommitted work. Fetch only when authorized under the current environment. Verify the actual tips of `origin/preview` and `origin/main`, their common history, open PRs, branch protection, merge policy, and repository automatic branch deletion settings. Verify the real production deployment workflow, target and environment, as well as the separate preview deployment. Read `docs/hosting.md` but confirm the live configuration; do not assume it is up to date.
2. The original remote `main` and `preview` histories were unrelated; local `preview` has since been rebased onto `main`, but the remote may not yet reflect that. Check the remote histories rather than assuming. GitHub cannot open a normal PR across unrelated histories. If needed, explain the blocker and prepare a safe plan for an explicitly authorized history update that preserves both branches and the existing preview. Never force-push without explicit authorization, silently replace `main`, or change DNS. Do not present a PR on another branch as the requested preview-to-main PR. Production hosting also requires an explicitly authorized setup.
3. Confirm that merging cannot delete `preview`: inspect automatic branch deletion and the chosen merge procedure. If preservation cannot be guaranteed, stop and resolve it with the owner before merging. Never change repository settings without authorization. Verify that production builds deploy the intended site artifact and do not overwrite the preview destination. If a working production target or trigger is missing, prepare a concrete setup plan; do not claim a deployment will occur.

## Prepare and review

4. Compare the exact remote `preview` and `main` tips and identify everything being released, including content, configuration and dependencies. Confirm pending work is committed to `preview`, check the intended changes and run `rtk npm run check`. Investigate failures before proceeding. Verify the preview site as appropriate for the changed content, including desktop and mobile layouts. Avoid adding unrelated local changes to the release.
5. Write clear French release notes for the editor based on the actual changes, with technical details and validation in the PR where useful. Identify any unfinished or draft content and deployment limitations; do not invent changes. Explain the proposed production impact and provide the preview link.
6. With authorization for the relevant remote changes, push only the intended commits to `preview` if necessary and create or update a PR explicitly from `preview` to `main`. Link the PR and provide its title, release notes, checks and exact source commit for review. An instruction merely to prepare or create a PR is not authorization to merge it or change production.

## Publish

7. Merge only when the owner explicitly authorizes publishing or merging this reviewed release. Check that the PR head and base have not changed since review, required checks pass, and merging will preserve `preview`. If they changed, update the review and obtain approval for the revised release. Follow branch protections; do not bypass them or enable auto-merge without explicit authorization.
8. Merge the PR without deleting `preview`. Let the configured production workflow run; if its actual setup requires a separate dispatch, do so only when covered by the publication authorization. Monitor the real run through completion, verify the deployed production site and confirm the preview branch and deployment still exist. Report the PR, merge commit, workflow result, live URL and any failure. Never claim publication based only on a successful merge.
