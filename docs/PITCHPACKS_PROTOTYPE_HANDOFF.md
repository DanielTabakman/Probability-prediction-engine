# PitchPacks prototype handoff

## Purpose
This is the smallest playable mechanics prototype for the NFL version of PitchPacks. The next pass should be visual/aesthetic, not a redesign of the game loop.

## Current mechanics — do not change during the visual pass
- 5 active players + 1 rotating bench player.
- Player chooses the six before the battle; the other six roster cards lock once combat starts.
- Players may be freely positioned in the user's half before combat.
- During combat, drag the bench card onto an active player to swap. The pulled player becomes the new bench. Swap cooldown: 6 seconds.
- Player-facing stats are intentionally only **ATK** and **HP**.
- QB = ranged main DPS.
- OL = rusher; prioritizes the enemy QB.
- DL = protector; stays near its own QB, attacks nearby threats, and reduces damage to the QB while close.
- No special QB-knockout penalty. Losing the main DPS is punishment enough.
- Win condition: beat the snot out of everyone on the other team.
- Simulated NFL plays add a small rest-of-match modifier plus a larger next-battle modifier.
- Enough accumulated heat makes a player enter the next battle **ON FIRE**; on-fire players visibly burn and deal small nearby AOE burn damage.
- Battles are manually started during TV downtime. There is no forced every-N-minutes battle timer.

## Hidden implementation values
Movement speed, attack range, and attack cooldown exist only so the roles behave differently. They are not player-facing stats yet and should not be promoted into the UI during the visual pass.

## Visual-pass goal
Make the little football players easy and fun to watch while preserving legibility:
- enemy team top, user team bottom;
- QB immediately recognizable;
- rusher vs protector behavior readable without explanation;
- hits, HP loss, knockouts, fire state, and bench swaps obvious;
- ATK and HP readable at a glance.

## Five-minute test sequence
1. Click **Quick lineup**.
2. Select a player and click **Start TV plays**.
3. Let enough fake plays accumulate that the player will enter the next fight on fire.
4. Start the battle.
5. Watch OL rush the opposing QB and DL protect its own QB.
6. Drag the bench card onto an active player to rotate the bench.
7. Confirm ATK / HP remain readable as HP falls and buffs change ATK.
8. Confirm knocked-out players are visually obvious.
9. Finish the fight and use **Back to TV / Setup**.

## Source of truth
The live prototype uses exactly these files:
- `apps/msos-web/public/daniel/pitchpacks-game.html`
- `apps/msos-web/public/daniel/pitchpacks-game.css`
- `apps/msos-web/public/daniel/pitchpacks-game.js`

The Next.js route is:
- `apps/msos-web/src/app/daniel/pitchpacks/page.tsx`
