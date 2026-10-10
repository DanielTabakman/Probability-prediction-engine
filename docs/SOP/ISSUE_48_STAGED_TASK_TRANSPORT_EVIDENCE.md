# Issue 48 Staged Task Transport Evidence

Immutable incident evidence from the second real Windows handoff:

- Attempted reviewed commit: `cb2bef253757cfad3136a5419f1c7f64ce2f79bb`
- Expected old bootstrap: `d3f6029faf992fc8609dd4ee69773cd6f2068917`
- All seven old-bootstrap canonical provenance checks passed.
- All new-checkout canonical Git-blob checks passed.
- Staged raw hashes matched new-checkout raw hashes.
- Staged PowerShell parser passed.
- `staged Python to PowerShell states transport` failed with a Python traceback.
- Activation performed: false.
- Rollback performed: false.
- Updater task restored: true, final state Ready.

Repair evidence:

- `src/msos_autobuilder/staged_task_transport.py` registers the staged supervisor module in `sys.modules` before `exec_module`.
- The previous `sys.modules` entry is restored, or the temporary entry is removed, in a `finally` block.
- `tests/test_msos_autobuilder_staged_task_transport.py` proves the old unregistered dynamic import fails against the real repository `src/msos_autobuilder/self_update_supervisor.py`.
- The same test proves the repaired subprocess probe succeeds for all five managed task names:
  - `PPE Headless Stack`
  - `PPE VM Watchdog`
  - `PPE VM Hygiene`
  - `PPE Network Watchdog`
  - `PPE Desktop Mirror Sync`
- The probe validates an in-memory `states` payload only. It does not read from or write to the installed machine Task Scheduler.
- `validation_results.output` retains complete stdout and stderr text, including full tracebacks when subprocess import fails. It is not collapsed to the first traceback line.

