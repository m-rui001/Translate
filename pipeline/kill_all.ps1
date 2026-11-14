Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -like '*run.py*' -or $_.CommandLine -like '*fill_gaps*' -or $_.CommandLine -like '*supervise*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 3
@(Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -like '*run.py*' -or $_.CommandLine -like '*fill_gaps*' -or $_.CommandLine -like '*supervise*' }).Count
