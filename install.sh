#!/usr/bin/env bash
set -euo pipefail

BIN_DIR="$HOME/.local/bin"
LIB_DIR="$HOME/.local/lib/weather-cli"

mkdir -p "$BIN_DIR" "$LIB_DIR"

cp -r weather_cli "$LIB_DIR/"

cat > "$BIN_DIR/weather" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m weather_cli "$@"
SCRIPT

chmod +x "$BIN_DIR/weather"

echo "✅ weather-cli v2 terinstal!"
echo "   Jalankan: weather"
echo "   Pastikan $BIN_DIR ada di PATH"
