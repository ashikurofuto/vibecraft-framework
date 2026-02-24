# Tower Defense Game (Multiplayer)

## Idea
A browser-based multiplayer tower defense game where 2-4 players
cooperate to defend a base against waves of enemies.
Players can place towers, upgrade them, and use special abilities.

## Goals
- Real-time cooperative multiplayer (2-4 players)
- At least 5 tower types with upgrade paths
- 10+ enemy types with different behaviours
- Wave-based progression with a boss every 5 waves
- Leaderboard per session

## Non-Goals
- Mobile native app (browser only)
- Account system / persistent progression (v1)
- More than 4 players simultaneously

## Users
- Casual gamers playing browser games with friends
- Session length: 20-40 minutes

## Risks
- WebSocket latency for real-time sync
- Performance with many enemies on screen
- State sync consistency across clients
