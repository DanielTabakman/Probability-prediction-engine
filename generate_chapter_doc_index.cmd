@echo off
setlocal
cd /d "%~dp0"
python "%CD%\scripts\generate_chapter_doc_index.py" --repo-root "%CD%" --write %*
