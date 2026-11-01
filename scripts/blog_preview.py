"""Manage an isolated, auto-refreshing local preview of one blog draft."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / '.blog-preview'
STATE_FILE = STATE_DIR / 'session.json'
LAST_FILE = STATE_DIR / 'last-draft.json'
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
REFRESH = b'''<script>(()=>{let v;let last=0;const ping=()=>{const now=Date.now();if(now-last>30000){last=now;fetch('/__blog_preview/activity',{method:'POST'}).catch(()=>{})}};for(const e of ['pointerdown','keydown','scroll','touchstart'])addEventListener(e,ping,{passive:true});document.addEventListener('visibilitychange',()=>{if(!document.hidden)ping()});const check=async()=>{try{const r=await fetch('/__blog_preview/version',{cache:'no-store'});const n=await r.text();if(v!==undefined&&v!==n)location.reload();v=n}catch{}};check();setInterval(check,2000)})();</script>'''


def state():
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return None


def control(session, action):
    request = urllib.request.Request(
        f"http://127.0.0.1:{session['port']}/__blog_preview/{action}",
        headers={'X-Preview-Token': session['token']},
        method='POST' if action in {'stop', 'activity'} else 'GET')
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            return json.load(response)
    except (OSError, ValueError, KeyError):
        return None


def available_port(port):
    """Prefer the previous URL, but never take over a different server."""
    try:
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(('127.0.0.1', port))
        return port
    except OSError:
        return 0


def serve(slug, port, idle_seconds, token):
    STATE_DIR.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='output-', dir=STATE_DIR))
    env = dict(os.environ, PSYTOURS_PREVIEW_DRAFT=slug)
    command = ['node', 'node_modules/@11ty/eleventy/cmd.cjs', '--watch', f'--output={output}']
    child = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL)
    last_activity = [time.monotonic()]
    stopping = [False]
    draft = ROOT / 'content/posts' / f'{slug}.md'
    last_edit = draft.stat().st_mtime_ns

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(output), **kwargs)

        def log_message(self, *_args):
            pass

        def response_json(self, code, value):
            body = json.dumps(value).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            path = urlsplit(self.path).path
            if path == '/__blog_preview/activity':
                # A local visible page may signal human activity; polling does not.
                last_activity[0] = time.monotonic()
                return self.response_json(200, {'ok': True})
            if path == '/__blog_preview/stop' and self.headers.get('X-Preview-Token') == token:
                stopping[0] = True
                return self.response_json(200, {'ok': True})
            self.response_json(404, {'error': 'not found'})

        def do_GET(self):
            request = urlsplit(self.path)
            if request.path == '/__blog_preview/status':
                if self.headers.get('X-Preview-Token') != token:
                    return self.response_json(403, {'error': 'forbidden'})
                return self.response_json(200, {'slug': slug, 'pid': os.getpid(), 'port': server.server_port})
            if request.path == '/__blog_preview/version':
                # Eleventy rewrites the selected HTML on edits; avoid treating
                # automatic reload polling as activity.
                page = output / 'post' / slug / 'index.html'
                version = str(page.stat().st_mtime_ns if page.exists() else 0).encode()
                self.send_response(200)
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(version)))
                self.end_headers()
                return self.wfile.write(version)
            relative = unquote(request.path).lstrip('/')
            target = (output / relative).resolve()
            if not target.is_relative_to(output.resolve()):
                return self.send_error(404)
            if target.is_dir():
                target /= 'index.html'
            if target.suffix == '.html' and target.is_file():
                last_activity[0] = time.monotonic()
                body = target.read_bytes().replace(b'</body>', REFRESH + b'</body>')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                return self.wfile.write(body)
            return super().do_GET()

    server = None
    try:
        server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
        server.timeout = 1
        session = {'pid': os.getpid(), 'port': server.server_port, 'slug': slug, 'token': token}
        STATE_FILE.write_text(json.dumps(session))
        os.chmod(STATE_FILE, 0o600)
        while not stopping[0] and child.poll() is None and time.monotonic() - last_activity[0] < idle_seconds:
            server.handle_request()
            try:
                edited = draft.stat().st_mtime_ns
                if edited != last_edit:
                    last_edit = edited
                    last_activity[0] = time.monotonic()
            except FileNotFoundError:
                pass
    finally:
        if server:
            server.server_close()
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        if state() and state().get('token') == token:
            STATE_FILE.unlink(missing_ok=True)
        shutil.rmtree(output, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    start = commands.add_parser('start')
    start.add_argument('slug')
    start.add_argument('--port', type=int, default=0, help='0 selects a free local port')
    start.add_argument('--idle-minutes', type=float, default=30)
    commands.add_parser('status')
    commands.add_parser('stop')
    commands.add_parser('touch')
    commands.add_parser('resume')
    internal = commands.add_parser('_serve', help=argparse.SUPPRESS)
    internal.add_argument('slug')
    internal.add_argument('port', type=int)
    internal.add_argument('idle_seconds', type=float)
    internal.add_argument('token')
    args = parser.parse_args()
    if args.command == '_serve':
        return serve(args.slug, args.port, args.idle_seconds, args.token)
    current = state()
    active = control(current, 'status') if current else None
    if args.command == 'resume':
        try:
            previous = json.loads(LAST_FILE.read_text())
            args.slug = previous['slug']
            args.port = available_port(int(previous['port'])) if not active else active['port']
            args.idle_minutes = float(previous['idle_minutes'])
        except (OSError, ValueError, KeyError, TypeError):
            parser.error('No previous blog draft is recorded; start the draft by slug')
        args.command = 'start'
    if args.command == 'start':
        if not SLUG.fullmatch(args.slug) or not (ROOT/'content/posts'/f'{args.slug}.md').is_file():
            parser.error('Choose the slug of an existing Markdown post in content/posts/')
        if not 0 <= args.port <= 65535 or args.idle_minutes <= 0:
            parser.error('Port must be 0–65535 and inactivity must be positive')
        if active:
            if active['slug'] != args.slug:
                parser.error('Another managed blog preview is running; stop it before starting a different draft')
            control(current, 'activity')
            print(f"Preview already running: http://localhost:{active['port']}/post/{args.slug}/")
            return
        STATE_DIR.mkdir(exist_ok=True)
        token = secrets.token_urlsafe(24)
        log = (STATE_DIR/'preview.log').open('a')
        process = subprocess.Popen([sys.executable, __file__, '_serve', args.slug, str(args.port),
                                    str(args.idle_minutes*60), token], cwd=ROOT, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        for _ in range(100):
            current = state()
            if current and current.get('token') == token and control(current, 'status'):
                url = f"http://localhost:{current['port']}/post/{args.slug}/"
                try:
                    with urllib.request.urlopen(url, timeout=1):
                        LAST_FILE.write_text(json.dumps({'slug': args.slug, 'port': current['port'],
                                                        'idle_minutes': args.idle_minutes}))
                        print(f'Preview: {url}\nStops after {args.idle_minutes:g} minutes of inactivity.\nLog: {STATE_DIR / "preview.log"}')
                        return
                except OSError:
                    pass
            if process.poll() is not None:
                break
            time.sleep(.2)
        if current and current.get('token') == token:
            control(current, 'stop')
        elif process.poll() is None:
            process.terminate()
        raise SystemExit(f'Preview did not start; inspect {STATE_DIR / "preview.log"}')
    if not active:
        print('No managed blog preview is running.')
        return
    if args.command == 'stop':
        if not control(current, 'stop'):
            raise SystemExit('Could not stop the managed preview')
        print('Managed blog preview stopped.')
    elif args.command == 'touch':
        control(current, 'activity')
        print('Preview inactivity timer refreshed.')
    else:
        print(f"Preview: http://localhost:{active['port']}/post/{active['slug']}/ (PID {active['pid']})")


if __name__ == '__main__':
    main()
