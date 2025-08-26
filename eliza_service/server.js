// // eliza_service/server.js
// import express from "express";
// import bodyParser from "body-parser";

// // TODO: Replace this placeholder with real ElizaOS agent call.
// // For now, it returns short, human-like replies.
// async function elizaReply({ message, history }) {
//   const text = (message || "").toLowerCase();
//   if (/^hi$|hello|hey/.test(text)) return "Hey! How’s your day going?";
//   if (text.includes("who are you")) return "Just a friend here to chat.";
//   if (text.includes("help")) return "Got you. What’s one small thing you want to change?";
//   return "I hear you. Tell me a bit more.";
// }

// const app = express();
// app.use(bodyParser.json());

// app.post("/reply", async (req, res) => {
//   try {
//     const { message, history = [] } = req.body || {};
//     const reply = await elizaReply({ message, history });
//     res.json({ text: reply });
//   } catch (e) {
//     console.error("Eliza error:", e);
//     res.status(500).json({ error: "eliza_error" });
//   }
// });

// const PORT = process.env.PORT || 5101;
// app.listen(PORT, () => console.log(`ElizaOS service running on port ${PORT}`));


// eliza_service/server.js
import express from "express";
import bodyParser from "body-parser";
import fs from "fs";
import path from "path";

const CONFIG_PATH = process.env.ELIZA_CONFIG || "app/eliza_service/eliza.config.json";

function loadToneConfig() {
  try {
    const raw = fs.readFileSync(CONFIG_PATH, "utf-8");
    const parsed = JSON.parse(raw);
    return parsed.style || {};
  } catch (e) {
    console.error("Tone config load error:", e);
    return {
      tone: "friendly",
      maxSentences: 2,
      rules: ["Use simple, everyday words.", "Avoid long explanations."]
    };
  }
}

function enforceTone(text, config) {
  if (!text || typeof text !== "string") return "I’m here for you. Let’s take a small step together.";

  const max = config.maxSentences || 2;
  const sentences = text.split(".").map(s => s.trim()).filter(Boolean);
  const trimmed = sentences.slice(0, max).join(". ") + ".";

  if (trimmed.split(" ").length < 4) return "I hear you. Want to share a bit more?";
  return trimmed;
}

async function elizaReply({ message, history }) {
  const config = loadToneConfig();
  const text = (message || "").toLowerCase();

  if (/^hi$|hello|hey/.test(text)) return enforceTone("Hey! How’s your day going?", config);
  if (text.includes("who are you")) return enforceTone("Just a friend here to chat.", config);
  if (text.includes("help")) return enforceTone("Got you. What’s one small thing you want to change?", config);
  if (!text || text.length < 3) return enforceTone("I’m here. Want to share what’s on your mind?", config);

  return enforceTone("I hear you. Tell me a bit more.", config);
}

const app = express();
app.use(bodyParser.json());

app.post("/reply", async (req, res) => {
  try {
    const { message, history = [] } = req.body || {};
    const reply = await elizaReply({ message, history });
    res.json({ text: reply });
  } catch (e) {
    console.error("Eliza error:", e);
    res.status(500).json({ error: "eliza_error" });
  }
});

const PORT = process.env.PORT || 5101;
app.listen(PORT, () => console.log(`ElizaOS service running on port ${PORT}`));