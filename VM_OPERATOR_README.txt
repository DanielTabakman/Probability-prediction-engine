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
4. VM_RESTART.cmd  — STOP + wait + START in one click (use instead of START alone)
5. VM_AUTO.cmd     — same as VM_RESTART (your "make it go" button on the VM)

Order when fixing problems:
  VM_STOP  ->  close blank windows by hand  ->  wait 30 seconds  ->  VM_START once
  Or just: VM_RESTART (does stop + wait + start for you)

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
DESKTOP BUILD     — only when phone says IDE_BUILD (opens Cursor on THIS pc)
DESKTOP CONTINUE  — only after a BUILD merged to main
DESKTOP STOP      — stop popups on this PC (run if you see blank cmd windows)

NO auto-loop on this PC. The VM runs the loop 24/7 (VM AUTO / VM RESTART on the VM).

Run setup_operator_shortcuts.cmd once to put BUILD/CONTINUE on your Desktop (also runs automatically from DESKTOP_BUILD / VM_UPDATE).


WHY COPY-PASTE FAILED
---------------------
- Win+R closes the window when the command finishes (you could not read status)
- Pasting START multiple times spawns multiple loops = popup storm
- "set ..." lines are not commands — they only belong inside .cmd files
