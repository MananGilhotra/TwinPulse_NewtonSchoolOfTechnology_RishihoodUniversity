#!/usr/bin/env bash
# Build the static live demo (twin runs in the browser) and publish it to the gh-pages branch.
set -euo pipefail
cd "$(dirname "$0")/.."
REPO_NAME=$(basename -s .git "$(git remote get-url origin)")
.venv/bin/python scripts/export_static.py
(cd dashboard && VITE_STATIC=1 VITE_BASE="/$REPO_NAME/" npm run build --silent -- --outDir dist-pages --emptyOutDir)
touch dashboard/dist-pages/.nojekyll
TMP=$(mktemp -d)
cp -R dashboard/dist-pages/. "$TMP"/
cd "$TMP"
git init -q -b gh-pages
git add -A
git -c user.name="Manan Gilhotra" -c user.email="179332727+MananGilhotra@users.noreply.github.com" commit -q -m "Deploy NightTwin live demo"
git push -q -f "$(cd - >/dev/null; git remote get-url origin)" gh-pages
echo "Deployed: https://$(git -C "$OLDPWD" remote get-url origin | sed -E 's#https://github.com/([^/]+)/.*#\1#' | tr 'A-Z' 'a-z').github.io/$REPO_NAME/"
