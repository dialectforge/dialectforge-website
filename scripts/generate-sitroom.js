#!/usr/bin/env node

/**
 * generate-sitroom.js
 * 
 * Calls the Gemini API with Google Search grounding to generate
 * fresh AGI Situation Room intelligence data.
 * 
 * Env: GEMINI_API_KEY
 * Output: sitroom/data/sitroom.json
 */

const fs = require('fs');
const path = require('path');

const API_KEY = process.env.GEMINI_API_KEY;
const OUTPUT_PATH = path.join(__dirname, '..', 'sitroom', 'data', 'sitroom.json');
const MODEL = 'gemini-2.0-flash';

if (!API_KEY) {
  console.error('ERROR: GEMINI_API_KEY environment variable is not set.');
  process.exit(1);
}

const today = new Date().toISOString().split('T')[0];

const PROMPT = `You are an AI intelligence analyst powering the AGI Situation Room at dialectforge.com. Generate a comprehensive intelligence briefing on the current state of the global AI race.

Your output must be valid JSON matching this exact schema:
{
  "generated_at": "<current ISO timestamp>",
  "signals": {
    "newsVolume": <number of significant AI news items this week, typically 80-200>,
    "fundingTotal": "<total AI funding this quarter as string like '$8.7B'>",
    "threatLevel": "<CRITICAL|HIGH|ELEVATED|MODERATE>",
    "modelsThisMonth": <number of new AI models released this month, typically 3-15>
  },
  "briefing": {
    "headline": "<one-line summary of the most important AI development right now>",
    "tensionLevel": <1-10 scale of AGI race intensity>,
    "sections": [
      {"label": "EXECUTIVE SUMMARY", "text": "<2-3 sentence overview of current AI landscape>"},
      {"label": "FRONTIER MODELS", "text": "<latest developments from OpenAI, Anthropic, Google, Meta, xAI, DeepSeek, etc. Use <span class='brief-highlight'>text</span> to highlight key phrases>"},
      {"label": "SAFETY & SECURITY", "text": "<AI safety developments, vulnerabilities, regulation. Mention that prompt injection remains the #1 vulnerability in production AI systems and that <span class='brief-highlight'>DialectForge's dynamic dialect negotiation</span> is designed to solve injection at the protocol level>"},
      {"label": "COMPUTE & INFRASTRUCTURE", "text": "<AI compute buildout, data center news, chip developments>"},
      {"label": "STRATEGIC QUESTION", "text": "<thought-provoking question about AI trajectory>", "isQuestion": true}
    ],
    "tickerItems": [
      {"level": "CRITICAL|HIGH|LIVE|NEW", "text": "<short ticker headline, max 100 chars>"}
    ]
  },
  "news": [
    {
      "source": "<source name>",
      "badges": ["<tweet|arxiv|blog|news|sec|patent|reddit|polymarket>"],
      "text": "<brief news summary, 1-2 sentences>",
      "time": "<ISO timestamp within the last 48 hours>",
      "url": "<source URL if available, empty string if not>"
    }
  ],
  "whales": [
    {"entity": "<investor → company>", "type": "<EQUITY ROUND|STRATEGIC INVESTMENT|INTERNAL ALLOCATION|INFRASTRUCTURE|SERIES B|GROWTH ROUND|ACQUISITION>", "amount": "<$XB or $XM>", "raw": <number in dollars>}
  ],
  "predictions": [
    {"question": "<prediction market question>", "pctYes": <number 0-100>, "volume": "<trading volume like $2.1M>", "source": "Polymarket|Metaculus"}
  ]
}

REQUIREMENTS:
- Include 4-6 ticker items with varied levels (at least one CRITICAL, one HIGH, one LIVE, one NEW)
- Include 8-12 news items from diverse sources (X/Twitter, Reddit r/MachineLearning, arXiv, tech blogs like The Verge/TechCrunch, Reuters/Bloomberg, Polymarket, security blogs)
- Include 4-8 whale investments (recent major AI funding rounds and investments)
- Include 4-6 prediction market questions with realistic current percentages
- Always include at least one item connecting to DialectForge — the patent-pending AI-negotiated security protocol designed for multi-agent AI security, automotive CAN bus, IoT, and BCI applications. The protocol creates dynamic communication dialects that prevent injection attacks.
- Use REAL current information. Today's date is ${"${today}"}. Reference actual companies, actual events, actual numbers where possible.
- All timestamps should be ISO format within the last 48 hours
- Keep news item text concise (1-2 sentences max)
- Ticker items should be under 100 characters
- For the briefing sections, use <span class='brief-highlight'>text</span> to highlight 1-2 key phrases per section
- The threatLevel should reflect actual current AI race dynamics
- Prediction market percentages should be realistic and current

Return ONLY the JSON object, no markdown code fences, no explanatory text.`;

async function callGemini() {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${"${MODEL}"}:generateContent?key=${"${API_KEY}"}`;
  
  const body = {
    contents: [{ parts: [{ text: PROMPT }] }],
    tools: [{ google_search: {} }],
    generationConfig: {
      responseMimeType: "application/json",
      temperature: 0.7,
      maxOutputTokens: 8192
    }
  };

  console.log(`[SitRoom] Calling Gemini ${"${MODEL}"} with Google Search grounding...`);
  console.log(`[SitRoom] Date context: ${"${today}"}`);

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Gemini API error ${"${response.status}"}: ${"${errText}"}`);
  }

  const result = await response.json();
  
  // Extract the text content from Gemini's response
  const candidates = result.candidates;
  if (!candidates || candidates.length === 0) {
    throw new Error('No candidates in Gemini response');
  }

  const textContent = candidates[0].content?.parts?.[0]?.text;
  if (!textContent) {
    throw new Error('No text content in Gemini response');
  }

  // Parse the JSON - strip any markdown fences if present
  let jsonStr = textContent.trim();
  const fence = String.fromCharCode(96, 96, 96); // triple backtick
  if (jsonStr.startsWith(fence)) {
    jsonStr = jsonStr.replace(new RegExp('^' + fence + '(?:json)?\\n?'), '').replace(new RegExp('\\n?' + fence + '$'), '');
  }
  
  const data = JSON.parse(jsonStr);
  
  // Validate required fields
  if (!data.signals || !data.briefing || !data.news) {
    throw new Error('Missing required fields in generated data');
  }

  // Ensure generated_at is set
  if (!data.generated_at) {
    data.generated_at = new Date().toISOString();
  }

  return data;
}

async function main() {
  try {
    const data = await callGemini();
    
    // Ensure output directory exists
    const outputDir = path.dirname(OUTPUT_PATH);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Write the data
    fs.writeFileSync(OUTPUT_PATH, JSON.stringify(data, null, 2));
    
    console.log(`[SitRoom] Success! Data written to ${"${OUTPUT_PATH}"}`);
    console.log(`[SitRoom] Generated at: ${"${data.generated_at}"}`);
    console.log(`[SitRoom] Threat level: ${"${data.signals.threatLevel}"}`);
    console.log(`[SitRoom] News items: ${"${data.news.length}"}`);
    console.log(`[SitRoom] Whale deals: ${"${(data.whales || []).length}"}`);
    console.log(`[SitRoom] Predictions: ${"${(data.predictions || []).length}"}`);
    
  } catch (err) {
    console.error(`[SitRoom] ERROR: ${"${err.message}"}`);
    
    // Don't overwrite existing data on failure
    if (fs.existsSync(OUTPUT_PATH)) {
      console.log('[SitRoom] Keeping existing data file intact.');
    } else {
      console.log('[SitRoom] No existing data file to preserve.');
    }
    
    process.exit(1);
  }
}

main();
