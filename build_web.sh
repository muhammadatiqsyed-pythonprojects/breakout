#!/bin/bash
# Builds the web version from a clean copy and puts it in docs/ for GitHub Pages
set -e
rm -rf ../breakout_web
mkdir ../breakout_web
cp main.py ../breakout_web/
cp -r assets ../breakout_web/
pygbag --build --app_name breakout ../breakout_web
rm -rf docs
mkdir docs
cp -r ../breakout_web/build/web/. docs/
echo "Done. Now run: git add . and git commit and git push"