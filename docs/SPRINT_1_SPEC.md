# Sprint 1 Spec — One-Screen Manual Lab

## Goal
Turn the current prototype into a clean, understandable manual exploration tool.

## User story
As a user, I want to immediately see:
1. what the market is implying
2. what belief or trade inputs I am changing
3. how the payoff changes
4. the key trade stats

## Required outcomes
- Chart is visible near the top without much scrolling
- Main layout is two columns:
  - left = controls
  - right = chart + summary
- Summary box shows:
  - strategy name
  - debit/credit
  - max gain
  - max loss
  - breakevens
  - fit quality if available
- Advanced math/calculations are hidden by default in expanders
- There is a clear mode switch for:
  - exact strikes
  - target payoff
- There is a clear belief view switch for:
  - market belief
  - user belief
  - compare

## Non-goals
- no new AI features
- no prediction market work
- no major new strategy logic unless needed for layout/state cleanup
- no framework migration

## Technical principle
All visible outputs should derive from centralized state rather than duplicated widget logic.

## Done when
A new user can understand the screen in about 15 seconds and answer:
- what the market thinks
- what I think
- what trade I am looking at
- what the payoff is