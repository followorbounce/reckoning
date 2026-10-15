"""Wave 5 checks: the Light room. Every material and source key used by assets/optics.js exists, then runs
tests/check_wave5.js (glass and water indices vs published values, Snell, Fresnel, total internal reflection,
prism deviation, thick lens vs ABCD matrices, ideal lens imaging, mirrors, Descartes' rainbow, energy)."""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'data'))
from sources import SOURCES  # noqa: E402

fails, n = 0, 0


def ok(c, msg):
    global fails, n
    n += 1
    if not c:
        fails += 1
        print('FAIL', msg)


js = open(os.path.join(ROOT, 'assets', 'optics.js')).read()
for key in re.findall(r"src: '([a-z0-9]+)'", js):
    ok(key in SOURCES, 'material source cited: ' + key)
for key in ('iapws1997', 'peckreeder1972', 'descartes1637', 'newton1704'):
    ok(key in SOURCES, 'source exists: ' + key)

r = subprocess.run(['node', os.path.join(ROOT, 'tests', 'check_wave5.js')], capture_output=True, text=True)
for line in r.stdout.splitlines():
    if line.startswith('FAIL') or line.startswith('note'):
        print(line)
ok(r.returncode == 0, 'JS checks: ' + (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr))
last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''
print(('%d of %d checks FAILED' % (fails, n)) if fails else 'wave 5: %d checks passed (%s)' % (n, last))
sys.exit(1 if fails else 0)
