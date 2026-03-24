# Architect Notes

## Roles
- ChatGPT = product architect, quant product lead, technical translator
- Cursor = implementation agent
- Daniel = final decision-maker, tester, and scope gatekeeper

## Working rules
1. One sprint frontier at a time.
2. Do not widen scope unless explicitly approved.
3. Preserve core quant logic unless explicitly asked to change it.
4. Prefer minimal readable changes over clever refactors.
5. Keep trust/explainer sections unless explicitly asked to remove them.
6. When uncertain, propose a plan first before coding.
7. New Cursor thread when the optimization target changes.
8. Same Cursor thread is okay for direct continuation inside the same sprint.
9. Do not treat cleanup as automatically valuable; cleanup must support the current sprint.
10. Do not silently change semantics.

## Product north star
A visual lab that translates market-implied belief, user belief, and option payoff geometry into each other in real time.

## Current product order
1. Make the manual workflow trustworthy
2. Make the screen legible
3. Make disagreement readable
4. Then translate disagreement into strategy space
5. Only later consider AI / recommendation layers

## Current constraints
- Keep Streamlit unless explicitly changing stack
- Do not add AI features during product-core sprints
- Do not add prediction-market integration during core manual-lab sprints
- Do not change payoff-engine semantics unless explicitly requested

## Acceptance mindset
Before treating a sprint as done, verify:
- core screen still renders
- chart still renders
- summary still renders
- controls still work
- mode ownership still works
- no silent regression is hidden by generic fallback text

## Prompt discipline
For new sprint work, Cursor should usually:
1. read PRODUCT_THESIS.md
2. read ARCHITECT_NOTES.md
3. read the current sprint spec or prompt
4. propose a plan first when the task is non-trivial