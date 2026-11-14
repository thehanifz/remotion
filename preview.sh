#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
cd /root/main-app/remotion

mkdir -p out/previews

echo "Mengambil preview still frame..."
npx remotion still src/index.ts CarrickVideo out/previews/scene1_frame35.jpg --frame=35
npx remotion still src/index.ts CarrickVideo out/previews/scene3_frame350.jpg --frame=350
npx remotion still src/index.ts CarrickVideo out/previews/scene5_frame700.jpg --frame=700

echo "Hasil preview:"
ls -lh out/previews/
