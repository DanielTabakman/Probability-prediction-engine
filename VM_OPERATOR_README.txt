PPE operator — simple guide (no copy-paste)
============================================

YOUR TWO MACHINES
-----------------
Desktop PC  = Cursor IDE BUILD only (no auto loop)
Hyper-V VM  = runs the operator loop 24/7 in the background

DO NOT use Win+R or paste long commands. Double-click files in File Explorer.


ON THE VM (folder: C:\Users\ppeloop\Probability-prediction-engine)
-------------------------------------------------------------------
0. VM_UPDATE.cmd   — double-click FIRST if files are missing or old (git pull)
1. VM_STOP.cmd     — run this FIRST if popups appear (or before any restart)
2. VM_STATUS.cmd   — check if loop is healthy (window stays open)
3. VM_START.cmd    — run ONCE after STOP, when you want the loop running

Order when fixing problems:
  VM_STOP  ->  close blank windows by hand  ->  wait 30 seconds  ->  VM_START once

If popups return after VM_START: run VM_STOP again and stop — ask for help.


"WINDOWS CAN'T FIND IT" — usually this mistake
----------------------------------------------
- In File Explorer, click the address bar and type ONLY:  cmd
  (then press Enter — a black window opens)
- Type commands ONLY in that black window — NOT in the address bar.
- Do NOT type git pull or check_vm_loop in the address bar.
- Easier: skip typing — double-click VM_UPDATE.cmd then VM_STATUS.cmd


ON THE DESKTOP (folder: C:\Users\USER\Desktop\Probability-prediction-engine)
----------------------------------------------------------------------------
DESKTOP_STOP.cmd  — run if this PC shows operator popups

Do NOT run VM_START or install_ppe_desktop_operator_task on the desktop.


WHY COPY-PASTE FAILED
---------------------
- Win+R closes the window when the command finishes (you could not read status)
- Pasting START multiple times spawns multiple loops = popup storm
- "set ..." lines are not commands — they only belong inside .cmd files
