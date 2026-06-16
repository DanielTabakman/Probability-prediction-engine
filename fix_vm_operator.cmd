@echo off
setlocal
REM VM loop-host recovery: clean operator doc drift, mark product ready, run relay once.
REM Usage (on VM):  cd C:\Users\ppeloop\Probability-prediction-engine  &&  fix_vm_operator.cmd

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

echo [fix_vm_operator] restore operator docs from HEAD...
git restore docs/SOP/ACTIVE_PHASE_MANIFEST.json docs/SOP/PHASE_CHAPTER_BACKLOG.json docs/SOP/PHASE_QUEUE.json docs/SOP/PHASE_SELECTION_ROADMAP.json 2>nul
git checkout HEAD -- docs/SOP/ACTIVE_PHASE_MANIFEST.json docs/SOP/PHASE_CHAPTER_BACKLOG.json docs/SOP/PHASE_QUEUE.json docs/SOP/PHASE_SELECTION_ROADMAP.json 2>nul

echo [fix_vm_operator] validate roadmap JSON...
python -c "import json; json.load(open('docs/SOP/PHASE_SELECTION_ROADMAP.json',encoding='utf-8-sig')); print('roadmap ok')" || (
  echo [fix_vm_operator] roadmap corrupt — resetting all docs/SOP from origin/main
  git fetch origin main
  git checkout origin/main -- docs/SOP/ACTIVE_PHASE_MANIFEST.json docs/SOP/PHASE_CHAPTER_BACKLOG.json docs/SOP/PHASE_QUEUE.json docs/SOP/PHASE_SELECTION_ROADMAP.json
)

echo [fix_vm_operator] mark production wiring product slice ready...
call "%CD%\mark_ide_product_ready.cmd" MSOS-ProdWireV1-Product-Slice002 docs/SOP/PHASE_PLANS/msos_production_wiring_v1_relay.json
if errorlevel 1 (
  echo [fix_vm_operator] prod-wire mark failed — trying workflow slice marker...
  call "%CD%\mark_ide_product_ready.cmd" MSOS-WorkflowV1-Product-Slice002 docs/SOP/PHASE_PLANS/msos_workflow_persistence_v1_relay.json
)

echo [fix_vm_operator] run relay once...
call "%CD%\run_ppe_local.cmd"
exit /b %ERRORLEVEL%
