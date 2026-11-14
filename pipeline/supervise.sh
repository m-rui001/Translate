#!/usr/bin/env bash
# Keep the four translation shards alive. Usage: bash pipeline/supervise.sh
set -u
cd "$(dirname "$0")"
LOGDIR=../work
for sh in 0 1; do
  while true; do
    alive=$(powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | Where-Object {\$_.CommandLine -like '*run.py*shard $sh/2*'} | Measure-Object | Select-Object -ExpandProperty Count" 2>/dev/null | tr -d '\r')
    if [ "${alive:-0}" -lt 1 ]; then
      echo "$(date '+%H:%M:%S') shard $sh restart" >> "$LOGDIR/supervisor.log"
      # health-check the gateway; restart it if the port is dead
      if [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:8317/v1/models)" = "000" ]; then
        (cd /e/tools/freeai/cliproxy && nohup ./cli-proxy-api.exe -config config.yaml >> server.log 2>&1 &)
        sleep 10
      fi
      nohup env PYTHONIOENCODING=utf-8 DADEUMI_LEAN=1 DADEUMI_EXPR=0 DADEUMI_SECOND=0 DADEUMI_POLISH=0 \
        python run.py --chapters all --shard $sh/2 --workers 2 --target 1500 --polisher ox:gpt-6.1-sol \
        > "$LOGDIR/run_$sh.log" 2>&1 &
      disown
    fi
    sleep 120
  done &
done
wait
