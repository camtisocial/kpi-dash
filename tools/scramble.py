"""
Normalizes each column in shared/kpi-data.js to a 0–100 index scale
and adds ±7% jitter so values aren't reversible.
Run from project root: python3 tools/scramble.py
"""
import re, random, os

random.seed(99)
ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_JS = os.path.join(ROOT, 'shared', 'kpi-data.js')

# Column indices in RAW (0=date, 1–8 are numeric)
COLS = [1, 2, 3, 4, 5, 6, 7, 8]

def jitter(v, pct=0.07):
    return v * (1 + random.uniform(-pct, pct))

def parse_nullable(s):
    return None if s.strip() == 'null' else int(s.strip())

def fmt(v):
    return 'null' if v is None else str(int(round(v)))

src = open(DATA_JS).read()

# Extract RAW block
block_re = re.compile(r'(const RAW = \[)(.*?)(\];)', re.DOTALL)
match = block_re.search(src)
if not match:
    raise SystemExit("Could not find RAW array in kpi-data.js")

row_re = re.compile(
    r'\["([^"]+)",\s*'
    r'([\d]+|null),\s*([\d]+|null),\s*([\d]+|null),\s*'
    r'([\d]+|null),\s*([\d]+|null),\s*([\d]+|null),\s*'
    r'([\d]+|null),\s*([\d]+|null)\s*\]'
)

rows = []
for m in row_re.finditer(match.group(2)):
    rows.append([m.group(1)] + [parse_nullable(m.group(i)) for i in range(2, 10)])

# Find max per column (ignore nulls and zeros)
maxes = {}
for col in COLS:
    vals = [r[col] for r in rows if r[col] is not None and r[col] > 0]
    maxes[col] = max(vals) if vals else 1

# Normalize each column to 0–100 with jitter
for row in rows:
    for col in COLS:
        if row[col] is not None and row[col] > 0:
            normalized = (row[col] / maxes[col]) * 100
            row[col] = max(1, int(round(jitter(normalized))))
        elif row[col] == 0:
            row[col] = 0

# Write back
new_rows = []
for r in rows:
    vals = ', '.join(fmt(v) for v in r[1:])
    new_rows.append(f'  ["{r[0]}", {vals}]')

new_block = '\n' + ',\n'.join(new_rows) + '\n'
new_src = src[:match.start(2)] + new_block + src[match.end(2):]
open(DATA_JS, 'w').write(new_src)

print(f"Normalized {len(rows)} rows to 0–100 scale → {DATA_JS}")
