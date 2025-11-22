import { db, auth } from '../firebase';
import { doc, collection, onSnapshot, query, orderBy } from 'firebase/firestore';

// Base URL for Cloud Functions
const FUNCTIONS_URL = import.meta.env.VITE_FUNCTIONS_URL || 
  `http://127.0.0.1:5001/${import.meta.env.VITE_FIREBASE_PROJECT_ID || 'impostor-6320a'}/us-central1`;

/**
 * Helper to make authenticated requests to Firebase Cloud Functions
 */
async function callFunction(functionName, data = {}) {
  const user = auth.currentUser;
  if (!user) {
    throw new Error('User not authenticated');
  }

  const idToken = await user.getIdToken();
  
  const response = await fetch(`${FUNCTIONS_URL}/${functionName}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${idToken}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Request failed');
  }

  return response.json();
}

/**
 * Creates a new room
 */
export async function createRoom(playerName, source = 'web') {
  return callFunction('create_room', { playerName, source });
}

/**
 * Joins an existing room
 */
export async function joinRoom(roomId, playerName, source = 'web') {
  return callFunction('join_room', { roomId, playerName, source });
}

/**
 * Starts the game
 */
export async function startGame(roomId) {
  return callFunction('start_game', { roomId });
}

/**
 * Restarts the game
 */
export async function restartGame(roomId) {
  return callFunction('restart_game', { roomId });
}



/**
 * Gets the next hint for the impostor
 */
export async function getNextHint(roomId) {
  return callFunction('get_next_hint', { roomId });
}

/**
 * Subscribes to room data
 */
export function subscribeRoom(roomId, callback) {
  const roomRef = doc(db, 'rooms', roomId);
  
  return onSnapshot(roomRef, (snapshot) => {
    if (snapshot.exists()) {
      callback({ id: snapshot.id, ...snapshot.data() });
    } else {
      callback(null);
    }
  }, (error) => {
    console.error('Error subscribing to room:', error);
    callback(null);
  });
}

/**
 * Subscribes to players in a room
 */
export function subscribePlayers(roomId, callback) {
  const playersRef = collection(db, 'rooms', roomId, 'players');
  const playersQuery = query(playersRef, orderBy('joinedAt', 'asc'));
  
  return onSnapshot(playersQuery, (snapshot) => {
    const players = snapshot.docs.map(doc => ({
      uid: doc.id,
      ...doc.data()
    }));
    callback(players);
  }, (error) => {
    console.error('Error subscribing to players:', error);
    callback([]);
  });
}

/**
 * Subscribes to the current user's secret in a room
 */
export function subscribeMySecret(roomId, uid, callback) {
  const secretRef = doc(db, 'rooms', roomId, 'secrets', uid);
  
  return onSnapshot(secretRef, (snapshot) => {
    if (snapshot.exists()) {
      callback(snapshot.data());
    } else {
      callback(null);
    }
  }, (error) => {
    console.error('Error subscribing to secret:', error);
    callback(null);
  });
}
