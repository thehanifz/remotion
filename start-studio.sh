#!/bin/bash
# Remotion Studio launcher — /root/main-app/remotion
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
cd /root/main-app/remotion
exec npx remotion studio src/index.ts --port=3030 --no-open
