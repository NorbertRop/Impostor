# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER DEVICES                            │
│                                                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Browser  │    │ Browser  │    │ Browser  │              │
│  │  (Host)  │    │(Player2) │    │(Player3) │              │
│  └─────┬────┘    └─────┬────┘    └─────┬────┘              │
│        │               │               │                     │
└────────┼───────────────┼───────────────┼─────────────────────┘
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Firebase (Google Cloud)     │
         │                               │
         │  ┌─────────────────────────┐ │
         │  │   Anonymous Auth        │ │
         │  │  - Auto sign-in         │ │
         │  │  - Unique UID per device│ │
         │  └─────────────────────────┘ │
         │                               │
         │  ┌─────────────────────────┐ │
         │  │   Firestore Database    │ │
         │  │                         │ │
         │  │  rooms/                 │ │
         │  │    {roomId}/            │ │
         │  │      - hostUid          │ │
         │  │      - status           │ │
         │  │      - allowJoin        │ │
         │  │      players/           │ │
         │  │        {uid}/           │ │
         │  │          - name         │ │
         │  │          - isHost       │ │
         │  │          - seen         │ │
         │  │      secrets/           │ │
         │  │        {uid}/           │ │
         │  │          - role         │ │
         │  │          - word         │ │
         │  └─────────────────────────┘ │
         └───────────────────────────────┘
```

## Data Flow

### 1. Create Room Flow
```
Host Device                    Firebase
    │                             │
    │─────createRoom()────────────>│
    │                             │
    │<────roomId: "ABC123"────────│
    │                             │
    │──setDoc(rooms/ABC123)──────>│
    │                             │
    │──setDoc(players/hostUid)───>│
    │                             │
    │<────success─────────────────│
    │                             │
    │──subscribeRoom()───────────>│
    │<────real-time updates───────│
```

### 2. Join Room Flow
```
Player Device                  Firebase
    │                             │
    │─────joinRoom(code)─────────>│
    │                             │
    │<────getDoc(rooms/ABC123)────│
    │                             │
    │──setDoc(players/playerUid)─>│
    │                             │
    │──subscribeRoom()───────────>│
    │<────real-time updates───────│
    │                             │
All Connected Devices           │
    │<────players update──────────│
    │  (via real-time listeners)  │
```

### 3. Start Game Flow
```
Host Device                    Firebase                 Cloud Function         Other Players
    │                             │                          │                     │
    │─────startGame()────────────>│                          │                     │
    │                             │                          │                     │
    │──updateDoc(status='started')>│                          │                     │
    │                             │                          │                     │
    │                             │──onGameStart triggered──>│                     │
    │                             │                          │                     │
    │                             │                          │ [Pick impostor      │
    │                             │                          │  & word]            │
    │                             │                          │                     │
    │                             │<─setDoc(secrets/uid1)────│                     │
    │                             │<─setDoc(secrets/uid2)────│                     │
    │                             │<─setDoc(secrets/uid3)────│                     │
    │                             │                          │                     │
    │                             │<─updateDoc(status='dealt')│                     │
    │                             │                          │                     │
    │                             │────status update─────────────────────────────>│
    │                             │──secrets/uid available───────────────────────>│
```

### 4. Reveal Word Flow
```
Player Device                  Firebase
    │                             │
    │──subscribeMySecret()───────>│
    │<────secret data─────────────│
    │  { role, word }             │
    │                             │
    │ [User clicks "Show"]        │
    │                             │
    │ [User clicks "Seen"]        │
    │                             │
    │──updateDoc(seen=true)──────>│
    │                             │
    │<────success─────────────────│
    │                             │
All Devices                       │
    │<────player.seen update──────│
    │  (via subscribePlayers)     │
```

## Component Hierarchy

```
App (Router)
│
├── / (Home Route)
│   │
│   └── Setup
│       ├── Menu Mode
│       │   └── Create / Join buttons
│       ├── Create Mode
│       │   └── Create room button
│       └── Join Mode
│           └── Enter code & join
│
└── /r/:roomId (Room Route)
    │
    └── Room (Orchestrator)
        ├── status === 'lobby'
        │   └── Lobby
        │       ├── Room code display
        │       ├── Players list
        │       └── Host controls
        │           ├── Start game
        │           └── Lock/unlock join
        │
        └── status === 'dealt' || 'playing'
            └── Reveal
                ├── Pre-reveal
                │   └── "Show my role" button
                ├── Post-reveal
                │   ├── Role/word display
                │   └── "I've seen it" button
                └── Waiting
                    └── Ready counter
```

## State Management

### Local State (React useState)
- UI state (loading, errors, form inputs)
- Current view mode (menu/create/join)
- Revealed state (has player clicked reveal?)

### Firebase State (Real-time)
- Room data (status, hostUid, allowJoin)
- Players list (names, seen status)
- My secret (role, word) - private to each player

### Derived State
- `isHost` - computed from `room.hostUid === myUid`
- `seenCount` - computed from `players.filter(p => p.seen).length`
- `canStart` - computed from `isHost && players.length >= 3`

## Security Model

```
┌───────────────────────────────────────────────────────┐
│                  Firestore Security                   │
│                                                        │
│  PUBLIC (readable by all in room):                    │
│    ✓ rooms/{roomId}                                   │
│    ✓ rooms/{roomId}/players/{uid}                     │
│                                                        │
│  PRIVATE (readable only by owner):                    │
│    ✓ rooms/{roomId}/secrets/{uid}                     │
│      - Only that specific UID can read                │
│                                                        │
│  WRITE PERMISSIONS:                                   │
│    ✓ Host can: start game, update room, write secrets│
│    ✓ Players can: update own player doc              │
│    ✓ Anyone can: join room (if allowJoin=true)       │
│                                                        │
│  RULES ENFORCED BY:                                   │
│    - firestore.rules (server-side)                    │
│    - Authenticated users only (Anonymous Auth)        │
└───────────────────────────────────────────────────────┘
```

## Network Communication

### Real-time Listeners (WebSocket)
```javascript
// Firestore uses WebSockets for real-time updates
onSnapshot(docRef, (snapshot) => {
  // Automatically called when data changes
  // No polling, instant updates
});
```

### Write Operations (HTTPS)
```javascript
// All writes go through HTTPS REST API
setDoc(docRef, data);      // Create/overwrite
updateDoc(docRef, data);   // Partial update
```

## Performance Considerations

### Firestore Reads
- **Initial load**: ~3 reads (room + players + secret)
- **Per player join**: 1 read for all connected clients
- **Start game**: N reads + N writes (N = player count)
- **Per reveal**: 1 write

### Free Tier Limits
- 50,000 reads/day
- 20,000 writes/day
- 20,000 deletes/day
- 1 GB stored data
- 10 GB/month bandwidth

**Estimated capacity**: ~500-1000 games/day within free tier

### Optimization Strategies
- ✅ Use real-time listeners (no polling)
- ✅ Minimal document structure
- ✅ Client-side game logic (no server calls)
- ✅ Ephemeral data (rooms auto-expire via TTL policies)

## Scalability

### Current Architecture
- **Concurrent games**: Unlimited (within Firebase limits)
- **Players per game**: 3-20 (practical limit, not technical)
- **Simultaneous players**: Thousands (Firebase auto-scales)
- **Geographic**: Global (Firebase CDN)

### Bottlenecks
- None expected at moderate usage
- Firebase handles scaling automatically
- Free tier sufficient for hobby/small group use

### Future Scaling (if needed)
- Upgrade to Firebase Blaze plan (pay-as-you-go)
- Add caching layer (Redis)
- Implement room cleanup (delete old rooms)
- Add rate limiting per user

## Technology Stack

```
┌─────────────────────────────────────────┐
│            Frontend Stack               │
│                                         │
│  React 19           - UI Library        │
│  React Router 7     - Routing           │
│  Vite 7             - Build Tool        │
│  Firebase JS SDK 12 - Backend Client    │
│  CSS3               - Styling           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│            Backend Stack                │
│              (Firebase)                 │
│                                         │
│  Firestore          - Database          │
│  Firebase Auth      - Authentication    │
│  Firebase Hosting   - Static Hosting    │
│  Cloud Functions    - Game Logic        │
└─────────────────────────────────────────┘
```

## Deployment Architecture

```
┌──────────────────────────────────────────────────┐
│                  Production                      │
│                                                  │
│  ┌────────────────────┐                         │
│  │  CDN / Hosting     │                         │
│  │  (Vercel/Netlify)  │                         │
│  │                    │                         │
│  │  - Static HTML/CSS │                         │
│  │  - Bundled JS      │                         │
│  │  - words.txt       │                         │
│  └──────────┬─────────┘                         │
│             │                                    │
│             │ (User visits site)                 │
│             ▼                                    │
│  ┌────────────────────┐                         │
│  │   User Browser     │                         │
│  │                    │                         │
│  │  - Loads app       │                         │
│  │  - Connects to     │                         │
│  │    Firebase        │                         │
│  └──────────┬─────────┘                         │
│             │                                    │
│             │ (Firebase SDK calls)               │
│             ▼                                    │
│  ┌────────────────────┐                         │
│  │   Firebase Cloud   │                         │
│  │                    │                         │
│  │  - Auth            │                         │
│  │  - Firestore       │                         │
│  └────────────────────┘                         │
└──────────────────────────────────────────────────┘
```

## Error Handling

### Firebase Errors
- `permission-denied` → Check auth & rules
- `not-found` → Room doesn't exist
- `unavailable` → Network issue
- `unauthenticated` → Auth failed

### Application Errors
- Room code invalid → Show error, don't navigate
- < 3 players → Disable start button
- Connection lost → Show reconnecting message
- Rate limits → Exponential backoff

### Error Boundaries
- Component-level try-catch
- Global error boundary (TODO)
- Console errors for debugging
- User-friendly messages in UI

