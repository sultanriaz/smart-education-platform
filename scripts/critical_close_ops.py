"""Strict local Academic migration runner; uses existing private runtime .env files.

Commands: academic-migrate | permission-seed
Never regenerates env, seeds demo data, or touches Docker volumes.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.integration' / 'runtime'


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {'academic-migrate', 'permission-seed'}:
        print(__doc__)
        return 2
    action = sys.argv[1]
    name = 'academic' if action == 'academic-migrate' else 'identity'
    envfile = RUNTIME / f'{name}-service.env'
    if not envfile.is_file():
        print('ABORT: existing runtime env missing; do not run Configure.')
        return 2
    config = dotenv_values(envfile)
    if not config.get('DATABASE_URL'):
        print('ABORT: existing database URL missing.')
        return 2
    env = dict(os.environ)
    env.update({key: value for key, value in config.items() if value is not None})
    libs = [str(p) for p in (ROOT / 'libs/python').iterdir() if p.is_dir()]
    env['PYTHONPATH'] = os.pathsep.join([*libs, env.get('PYTHONPATH', '')])
    workdir = ROOT / 'services' / f'{name}-service'
    command = ([sys.executable, '-m', 'alembic', 'upgrade', 'head']
               if action == 'academic-migrate'
               else [sys.executable, '-m', 'app.scripts.seed_b01_permissions'])
    print(f'Executing {action} against existing {name} database; no credentials printed.', flush=True)
    return subprocess.run(command, cwd=workdir, env=env, check=False).returncode


if __name__ == '__main__':
    sys.exit(main())
