#!/bin/bash
# Poll polish_done.json counts; when all targets met, wait 10 min, then assemble.
DEADLINE=$(( $(date +%s) + 6*3600 ))
while true; do
  v3=$(ls /e/Translate/work_proust/out/v3/chunk*/polish_done.json 2>/dev/null | wc -l)
  v4=$(ls /e/Translate/work_proust/out/v4/chunk*/polish_done.json 2>/dev/null | wc -l)
  v6=$(ls /e/Translate/work_proust/out/v6/chunk*/polish_done.json 2>/dev/null | wc -l)
  v7=$(ls /e/Translate/work_proust/out/v7/chunk*/polish_done.json 2>/dev/null | wc -l)
  echo "$(date '+%F %T') v3=$v3/230 v4=$v4/178 v6=$v6/94 v7=$v7/130"
  if [ "$v3" -ge 230 ] && [ "$v4" -ge 178 ] && [ "$v6" -ge 94 ] && [ "$v7" -ge 130 ]; then
    echo "ALL COMPLETE. Waiting 10 min for quote fixes to settle..."
    sleep 600
    break
  fi
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    echo "TIMEOUT after 6h. Assembling with current final.txt."
    break
  fi
  sleep 300
done
cd /e/Translate && python pipeline_proust/assemble_proust.py
echo "ASSEMBLE_EXIT=$?"
