# Setting up an editor's computer

This guide is for the technical person preparing a computer for the Psy-Tours editor. The editor can then ask Codex in French to write or revise an article and review it in a browser.

## Prerequisites

- A supported Codex app or CLI, signed in and able to open this repository and use its project skills.
- Git, Node.js 22 or newer with npm, Python 3.9 or newer as `python3`, and RTK (`rtk`) on the PATH. Agents in this repository are instructed to prefix shell commands with `rtk`.
- A web browser and a writable local checkout. Network access is needed for the initial clone and dependency installation; the normal site build and local previews work offline.
- GitHub access to `9h41/psytours` for cloning and, separately, permission to push if the owner later authorizes a push. Do not share credentials with the editor or put them in the repository.

## Setup

1. Install the prerequisites and sign in to Codex. Clone the repository using an account with access, then check out `preview`:

   ```sh
   git clone https://github.com/9h41/psytours.git
   cd psytours
   git switch preview
   ```

   Leave `main` alone. SSH cloning is also fine if GitHub SSH access is configured.
2. In the repository directory, install the locked dependencies with `npm ci`.
3. Run `python3 scripts/doctor.py` (or `npm run doctor` once npm is available). Fix any reported missing items and run it again. The command only checks the local environment; it does not install software or change files.
4. Open the checkout in Codex. Confirm that the repository skill `psy-tours-blog-post` is available; restart Codex or reopen the project if it is not. Confirm the editor can open a local preview link in a browser.
5. For an end-to-end check, ask Codex in French to prepare a test draft, then review its preview and ask Codex to discard the test draft when done. Drafts stay out of normal builds. The dedicated preview refreshes on changes, stops after 30 minutes of inactivity and restarts when an unfinished writing conversation resumes.

The editor can simply ask: « Aide-moi à écrire un article sur… ». Codex handles the files and preview. Approving a draft for a local build does not authorize a commit, push or publication; these require the owner's explicit instructions. The site work remains on `preview`.

The doctor does not verify Codex sign-in or skill discovery, browser access, network connectivity, or GitHub permissions. Check these separately. `npm run check` runs the full site build and validation when needed; it is not required just to run the doctor.
