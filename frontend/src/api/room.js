import { 
  collection, 
  doc, 
  setDoc, 
  getDoc, 
  getDocs,
  updateDoc,
  deleteDoc, 
  onSnapshot,
  serverTimestamp,
  query,
  orderBy
} from 'firebase/firestore';
import { db, auth } from '../firebase';

export function generateRoomId() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let result = '';
  for (let i = 0; i < 6; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

export async function createRoom(playerName) {
  const roomId = generateRoomId();
  const uid = auth.currentUser.uid;
  
  const roomRef = doc(db, 'rooms', roomId);
  await setDoc(roomRef, {
    hostUid: uid,
    status: 'lobby',
    createdAt: serverTimestamp(),
    allowJoin: true
  });
  
  const playerRef = doc(db, 'rooms', roomId, 'players', uid);
  await setDoc(playerRef, {
    name: playerName,
    isHost: true,
    source: 'web',
    joinedAt: serverTimestamp(),
    seen: false,
    present: true
  });
  
  return roomId;
}

export async function joinRoom(roomId, playerName) {
  const uid = auth.currentUser.uid;
  
  const roomRef = doc(db, 'rooms', roomId);
  const roomSnap = await getDoc(roomRef);
  
  if (!roomSnap.exists()) {
    throw new Error('Room does not exist');
  }
  
  const roomData = roomSnap.data();
  if (!roomData.allowJoin) {
    throw new Error('Room is not accepting new players');
  }
  
  if (roomData.status !== 'lobby') {
    throw new Error('Game has already started');
  }
  
  const playerRef = doc(db, 'rooms', roomId, 'players', uid);
  await setDoc(playerRef, {
    name: playerName,
    isHost: false,
    source: 'web',
    joinedAt: serverTimestamp(),
    seen: false,
    present: true
  });
  
  return roomId;
}

export function subscribeRoom(roomId, callback) {
  const roomRef = doc(db, 'rooms', roomId);
  return onSnapshot(roomRef, (snapshot) => {
    if (snapshot.exists()) {
      callback({ id: snapshot.id, ...snapshot.data() });
    } else {
      callback(null);
    }
  });
}

export function subscribePlayers(roomId, callback) {
  const playersRef = collection(db, 'rooms', roomId, 'players');
  const q = query(playersRef, orderBy('joinedAt', 'asc'));
  
  return onSnapshot(q, (snapshot) => {
    const players = [];
    snapshot.forEach((doc) => {
      players.push({ uid: doc.id, ...doc.data() });
    });
    callback(players);
  });
}

export function subscribeMySecret(roomId, uid, callback) {
  const secretRef = doc(db, 'rooms', roomId, 'secrets', uid);
  return onSnapshot(secretRef, (snapshot) => {
    if (snapshot.exists()) {
      callback(snapshot.data());
    } else {
      callback(null);
    }
  });
}

export async function startGame(roomId) {
  const playersRef = collection(db, 'rooms', roomId, 'players');
  const playersSnap = await getDocs(playersRef);
  
  if (playersSnap.size < 2) {
    throw new Error('Need at least 3 players to start');
  }
  
  const roomRef = doc(db, 'rooms', roomId);
  await updateDoc(roomRef, {
    status: 'started'
  });
}

export async function markSeen(roomId, uid, seen) {
  const playerRef = doc(db, 'rooms', roomId, 'players', uid);
  await updateDoc(playerRef, {
    seen: seen
  });
}

export async function toggleAllowJoin(roomId, allow) {
  const roomRef = doc(db, 'rooms', roomId);
  await updateDoc(roomRef, {
    allowJoin: allow
  });
}

export async function resetGame(roomId) {
  const roomRef = doc(db, 'rooms', roomId);
  await updateDoc(roomRef, {
    status: 'lobby',
    allowJoin: true
  });
  
  const playersRef = collection(db, 'rooms', roomId, 'players');
  const playersSnap = await getDocs(playersRef);
  
  playersSnap.forEach(async (playerDoc) => {
    const playerRef = doc(db, 'rooms', roomId, 'players', playerDoc.id);
    await updateDoc(playerRef, {
      seen: false
    });
  });
}

export async function restartGame(roomId) {
  const playersRef = collection(db, 'rooms', roomId, 'players');
  const playersSnap = await getDocs(playersRef);
  
  const secretsRef = collection(db, 'rooms', roomId, 'secrets');
  const secretsSnap = await getDocs(secretsRef);
  
  const batch = [];
  
  playersSnap.forEach((playerDoc) => {
    const playerRef = doc(db, 'rooms', roomId, 'players', playerDoc.id);
    batch.push(updateDoc(playerRef, { seen: false }));
  });
  
  secretsSnap.forEach((secretDoc) => {
    batch.push(deleteDoc(secretDoc.ref));
  });
  
  await Promise.all(batch);
  
  const roomRef = doc(db, 'rooms', roomId);
  await updateDoc(roomRef, {
    status: 'started'
  });
}

