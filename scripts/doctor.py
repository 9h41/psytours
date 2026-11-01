"""Check local prerequisites for the Psy-Tours editorial workflow."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
problems = []


def report(ok, label, remedy):
    print(f"{'OK' if ok else 'MISSING'}  {label}")
    if not ok:
        print(f"         {remedy}")
        problems.append(label)


def command(name):
    return shutil.which(name)


def output(*args):
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return ''


def main():
    report(sys.version_info >= (3, 9), f'Python {sys.version.split()[0]} (3.9+)',
           'Install Python 3.9 or newer as python3.')
    node = command('node')
    version = output(node, '--version') if node else ''
    try:
        node_ok = int(version.lstrip('v').split('.')[0]) >= 22
    except ValueError:
        node_ok = False
    report(node_ok, f'Node.js {version or "not found"} (22+)', 'Install Node.js 22 or newer.')
    report(bool(command('npm')), 'npm', 'Install npm along with Node.js.')
    report(bool(command('git')), 'Git', 'Install Git.')
    report(bool(command('rtk')), 'RTK command-line tool',
           'Install RTK and make sure rtk is on PATH; see AGENTS.md.')
    report((ROOT / 'node_modules/@11ty/eleventy/cmd.cjs').is_file(), 'Eleventy dependencies',
           'From the repository, run: npm ci')
    report((ROOT / '.agents/skills/psy-tours-blog-post/SKILL.md').is_file(), 'Repository blog-writing skill',
           'Use a complete checkout of the preview branch.')
    report(os.access(ROOT, os.W_OK) and os.access(ROOT / 'content/posts', os.W_OK),
           'Writable checkout and posts directory', 'Give the editor write access to this checkout.')
    branch = output('git', 'branch', '--show-current') if command('git') else ''
    report(branch == 'preview', f'Git branch: {branch or "unknown"} (expected preview)',
           'Use the preview branch in a clean checkout.')
    print('\n' + (f'{len(problems)} item(s) need attention.' if problems else 'Local prerequisites are ready.'))
    print('Codex sign-in, skill availability in the app, browser access and GitHub permissions must be checked separately.')
    return bool(problems)


if __name__ == '__main__':
    sys.exit(main())
