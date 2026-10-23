#!/bin/bash
# Self-contained PeakMiner PRL installer/runner (no network needed for binary).
# Usage: bash installer.sh  [pool_url1 pool_url2 ...]
# Wallet + pools can be overridden via env: PEAK_USER, PEAK_WORKER, PEAK_URLS (space/colon separated)
set -u
BIN_DIR="$(cd "$(dirname "$0")" && pwd)"
PMLINUX="$BIN_DIR/linux/peakminer"
[ -x "$PMLINUX" ] || PMLINUX="$BIN_DIR/peakminer"
[ -x "$PMLINUX" ] || { echo "no local peakminer, will download"; PMLINUX=""; }
WORKER="${PEAK_WORKER:-h4nli-5090}"
USERS="${PEAK_USER:-prl1p08n7f9q0wwf8ykrgxrxrvlwcl8htpgs2da83zgtmfwzkdy6xwnvq4ndq96+4KCrDnn9dx6Xa57uzNjcmubgRGUuF1RZpgjvy8QKjCvNCAmMAt4CNeq}"
URLS=("${@:-}")
if [ ${#URLS[@]} -eq 0 ]; then
  URLS=(stratum+tcp://pearl-eu2.luckypool.io:3360 stratum+tcp://pearl-eu1.luckypool.io:3360 stratum+tcp://pearl-us-east.luckypool.io:3360)
fi
# Build --url args
urlargs=""; for u in "${URLS[@]}"; do urlargs="$urlargs --url $u"; done
echo "worker=$WORKER"
echo "urls=${URLS[*]}"
echo "bin=$PMLINUX"
echo "--- args preview ---"
echo "$PMLINUX $urlargs --user $USERS --coin pearl -w $WORKER --gpu-temp-stop0 78 --gpu-temp-start0 66"
