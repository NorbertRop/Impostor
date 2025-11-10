const {onSchedule} = require("firebase-functions/v2/scheduler");
const {onRequest} = require("firebase-functions/v2/https");
const {onDocumentUpdated} = require("firebase-functions/v2/firestore");
const admin = require("firebase-admin");
const fs = require("fs");
const path = require("path");

admin.initializeApp();

// Load word list from file
let WORDS = [];
try {
  const wordsPath = path.join(__dirname, "words.txt");
  const wordsContent = fs.readFileSync(wordsPath, "utf-8");
  WORDS = wordsContent.split("\n").filter((w) => w.trim().length > 0);
  console.log(`✅ Loaded ${WORDS.length} words from words.txt`);
} catch (error) {
  console.error("❌ Failed to load words.txt:", error);
  // Fallback words
  WORDS = ["kot", "pies", "dom", "drzewo", "słońce", "księżyc"];
}

/**
 * Select a random word from the word list
 */
function getRandomWord() {
  return WORDS[Math.floor(Math.random() * WORDS.length)];
}

/**
 * Select a random impostor from players
 */
function selectImpostor(players) {
  const playerIds = Object.keys(players);
  const randomIndex = Math.floor(Math.random() * playerIds.length);
  return playerIds[randomIndex];
}

/**
 * Scheduled function to clean up old rooms
 * Runs every 24 hours and removes rooms older than 24 hours
 */
exports.cleanupOldRooms = onSchedule("every 24 hours", async (event) => {
  const db = admin.firestore();
  const cutoffTime = new Date(Date.now() - 24 * 60 * 60 * 1000); // 24 hours ago

  console.log(`🧹 Starting cleanup of rooms older than ${cutoffTime.toISOString()}`);

  try {
    const roomsSnapshot = await db
        .collection("rooms")
        .where("createdAt", "<", cutoffTime)
        .get();

    if (roomsSnapshot.empty) {
      console.log("✅ No old rooms to clean up");
      return null;
    }

    const batch = db.batch();
    let deletedCount = 0;

    for (const roomDoc of roomsSnapshot.docs) {
      const roomId = roomDoc.id;
      console.log(`🗑️  Deleting room: ${roomId}`);

      // Delete subcollections
      const playersSnapshot = await roomDoc.ref.collection("players").get();
      playersSnapshot.docs.forEach((doc) => batch.delete(doc.ref));

      const secretsSnapshot = await roomDoc.ref.collection("secrets").get();
      secretsSnapshot.docs.forEach((doc) => batch.delete(doc.ref));

      // Delete room document
      batch.delete(roomDoc.ref);
      deletedCount++;
    }

    await batch.commit();
    console.log(`✅ Cleanup complete: ${deletedCount} room(s) deleted`);

    return {success: true, roomsDeleted: deletedCount};
  } catch (error) {
    console.error("❌ Cleanup error:", error);
    throw error;
  }
});

/**
 * Firestore trigger - automatically starts game when status changes to "started"
 * Assigns random word and selects impostor
 */
exports.onGameStart = onDocumentUpdated("rooms/{roomId}", async (event) => {
  const before = event.data.before.data();
  const after = event.data.after.data();
  const roomId = event.params.roomId;

  // Check if status changed to "started"
  if (before.status !== "started" && after.status === "started") {
    console.log(`🎮 Game starting for room: ${roomId}`);

    try {
      const db = admin.firestore();
      const roomRef = db.collection("rooms").doc(roomId);

      // Get all players
      const playersSnapshot = await roomRef.collection("players").get();
      const players = {};
      playersSnapshot.forEach((doc) => {
        players[doc.id] = doc.data();
      });

      const playerIds = Object.keys(players);

      if (playerIds.length < 3) {
        console.error("❌ Not enough players to start game");
        return null;
      }

      // Select random word and impostor
      const word = getRandomWord();
      const impostorId = selectImpostor(players);

      console.log(`📝 Selected word: ${word}`);
      console.log(`🎭 Selected impostor: ${impostorId}`);

      // Create secrets for each player
      const batch = db.batch();
      const secretsRef = roomRef.collection("secrets");

      for (const playerId of playerIds) {
        const player = players[playerId];
        const isImpostor = playerId === impostorId;

        const secret = {
          name: player.name,
          role: isImpostor ? "impostor" : "player",
          word: isImpostor ? null : word,
          discord_id: player.discord_id || null,
          createdAt: admin.firestore.FieldValue.serverTimestamp(),
        };

        batch.set(secretsRef.doc(playerId), secret);
      }

      // Update room with game info
      batch.update(roomRef, {
        word: word,
        impostorId: impostorId,
        startedAt: admin.firestore.FieldValue.serverTimestamp(),
      });

      await batch.commit();

      console.log(`✅ Game started successfully for room ${roomId}`);
      return {success: true, roomId, playerCount: playerIds.length};
    } catch (error) {
      console.error(`❌ Error starting game for room ${roomId}:`, error);
      throw error;
    }
  }

  return null;
});

/**
 * HTTP function for manual cleanup trigger
 * Can be called directly for testing or manual cleanup
 */
exports.manualCleanup = onRequest(async (req, res) => {
  const db = admin.firestore();
  const hoursParam = req.query.hours || "24";
  const hours = parseInt(hoursParam);

  if (isNaN(hours) || hours <= 0) {
    res.status(400).json({error: "Invalid hours parameter"});
    return;
  }

  const cutoffTime = new Date(Date.now() - hours * 60 * 60 * 1000);

  console.log(`🧹 Manual cleanup: rooms older than ${cutoffTime.toISOString()}`);

  try {
    const roomsSnapshot = await db
        .collection("rooms")
        .where("createdAt", "<", cutoffTime)
        .get();

    if (roomsSnapshot.empty) {
      res.json({
        message: "No old rooms to clean up",
        roomsDeleted: 0,
        hoursThreshold: hours,
      });
      return;
    }

    const batch = db.batch();
    let deletedCount = 0;

    for (const roomDoc of roomsSnapshot.docs) {
      const roomId = roomDoc.id;

      // Delete subcollections
      const playersSnapshot = await roomDoc.ref.collection("players").get();
      playersSnapshot.docs.forEach((doc) => batch.delete(doc.ref));

      const secretsSnapshot = await roomDoc.ref.collection("secrets").get();
      secretsSnapshot.docs.forEach((doc) => batch.delete(doc.ref));

      // Delete room document
      batch.delete(roomDoc.ref);
      deletedCount++;
    }

    await batch.commit();

    res.json({
      message: "Cleanup completed successfully",
      roomsDeleted: deletedCount,
      hoursThreshold: hours,
    });
  } catch (error) {
    console.error("❌ Manual cleanup error:", error);
    res.status(500).json({error: error.message});
  }
});

