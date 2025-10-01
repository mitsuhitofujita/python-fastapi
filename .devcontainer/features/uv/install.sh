#!/bin/bash
set -e

echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | env INSTALLER_NO_MODIFY_PATH=1 sh
# Move uv to system-wide location
mv "$HOME/.local/bin/uv" /usr/local/bin/uv
mv "$HOME/.local/bin/uvx" /usr/local/bin/uvx
echo "uv installed system-wide."
