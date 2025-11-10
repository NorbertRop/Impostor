const {onSchedule} = require("firebase-functions/v2/scheduler");
const {onRequest} = require("firebase-functions/v2/https");
const admin = require("firebase-admin");

admin.initializeApp();

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

