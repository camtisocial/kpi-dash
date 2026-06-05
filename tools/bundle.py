"""
Bundles a version's src/ files into self-contained Notion-ready HTML.
Inlines shared/kpi-style.css and shared/kpi-data.js into each file.

Usage (run from project root):
  python3 tools/bundle.py v2-sections
  python3 tools/bundle.py v3-widgets
"""
import os, re, sys

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.join(ROOT, 'shared')

def bundle(version):
    src  = os.path.join(ROOT, version, 'src')
    dist = os.path.join(ROOT, version, 'dist')
    os.makedirs(dist, exist_ok=True)

    css  = open(os.path.join(SHARED, 'kpi-style.css')).read()
    data = open(os.path.join(SHARED, 'kpi-data.js')).read()

    for fname in sorted(os.listdir(src)):
        if not fname.endswith('.html'):
            continue
        html = open(os.path.join(src, fname)).read()

        html = re.sub(
            r'<link rel="stylesheet" href="[^"]*kpi-style\.css">',
            f'<style>\n{css}\n</style>',
            html
        )
        html = re.sub(
            r'<script src="[^"]*kpi-data\.js"></script>',
            f'<script>\n{data}\n</script>',
            html
        )

        out = os.path.join(dist, fname)
        open(out, 'w').write(html)
        print(f'  {os.path.join(version, "dist", fname)}')

    print(f'Done — {version}/dist/ is ready for Notion upload.')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 tools/bundle.py <version-dir>')
        print('  e.g. python3 tools/bundle.py v2-sections')
        sys.exit(1)
    bundle(sys.argv[1])
