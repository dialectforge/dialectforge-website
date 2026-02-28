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

var fs = require('fs');
var path = require('path');

var API_KEY = process.env.GEMINI_API_KEY;
var OUTPUT_PATH = path.join(__dirname, '..', 'sitroom', 'data', 'sitroom.json');
var MODEL = 'gemini-2.0-flash';

if (!API_KEY) {
  console.error('ERROR: GEMINI_API_KEY environment variable is not set.');
  process.exit(1);
}

var today = new Date().toISOString().split('T')[0];

var PROMPT = 'You are an AI intelligence analyst powering the AGI Situation Room at dialectforge.com. Generate a comprehensive intelligence briefing on the current state of the global AI race.\n' +
'\n' +
'Your output must be valid JSON matching this exact schema:\n' +
'{\n' +
'  "generated_at": "<current ISO timestamp>",\n' +
'  "signals": {\n' +
'    "newsVolume": <number of significant AI news items this week, typically 80-200>,\n' +
'    "fundingTotal": "<total AI funding this quarter as string like \'$8.7B\'>",\n' +
'    "threatLevel": "<CRITICAL|HIGH|ELEVATED|MODERATE>",\n' +
'    "modelsThisMonth": <number of new AI models released this month, typically 3-15>\n' +
'  },\n' +
'  "briefing": {\n' +
'    "headline": "<one-line summary of the most important AI development right now>",\n' +
'    "tensionLevel": <1-10 scale of AGI race intensity>,\n' +
'    "sections": [\n' +
'      {"label": "EXECUTIVE SUMMARY", "text": "<2-3 sentence overview of current AI landscape>"},\n' +
'      {"label": "FRONTIER MODELS", "text": "<latest developments from OpenAI, Anthropic, Google, Meta, xAI, DeepSeek, etc. Use <span class=\'brief-highlight\'>text</span> to highlight key phrases>"},\n' +
'      {"label": "SAFETY & SECURITY", "text": "<AI safety developments, vulnerabilities, regulation. Mention that prompt injection remains the #1 vulnerability in production AI systems and that <span class=\'brief-highlight\'>DialectForge\'s dynamic dialect negotiation</span> is designed to solve injection at the protocol level>"},\n' +
'      {"label": "COMPUTE & INFRASTRUCTURE", "text": "<AI compute buildout, data center news, chip developments>"},\n' +
'      {"label": "STRATEGIC QUESTION", "text": "<thought-provoking question about AI trajectory>", "isQuestion": true}\n' +
'    ],\n' +
'    "tickerItems": [\n' +
'      {"level": "CRITICAL|HIGH|LIVE|NEW", "text": "<short ticker headline, max 100 chars>"}\n' +
'    ]\n' +
'  },\n' +
'  "news": [\n' +
'    {\n' +
'      "source": "<source name>",\n' +
'      "badges": ["<tweet|arxiv|blog|news|sec|patent|reddit|polymarket>"],\n' +
'      "text": "<brief news summary, 1-2 sentences>",\n' +
'      "time": "<ISO timestamp within the last 48 hours>",\n' +
'      "url": "<source URL if available, empty string if not>"\n' +
'    }\n' +
'  ],\n' +
'  "whales": [\n' +
'    {"entity": "<investor -> company>", "type": "<EQUITY ROUND|STRATEGIC INVESTMENT|INTERNAL ALLOCATION|INFRASTRUCTURE|SERIES B|GROWTH ROUND|ACQUISITION>", "amount": "<$XB or $XM>", "raw": <number in dollars>}\n' +
'  ],\n' +
'  "predictions": [\n' +
'    {"question": "<prediction market question>", "pctYes": <number 0-100>, "volume": "<trading volume like $2.1M>", "source": "Polymarket|Metaculus"}\n' +
'  ]\n' +
'}\n' +
'\n' +
'REQUIREMENTS:\n' +
'- Include 4-6 ticker items with varied levels (at least one CRITICAL, one HIGH, one LIVE, one NEW)\n' +
'- Include 8-12 news items from diverse sources (X/Twitter, Reddit r/MachineLearning, arXiv, tech blogs like The Verge/TechCrunch, Reuters/Bloomberg, Polymarket, security blogs)\n' +
'- Include 4-8 whale investments (recent major AI funding rounds and investments)\n' +
'- Include 4-6 prediction market questions with realistic current percentages\n' +
'- Always include at least one item connecting to DialectForge -- the patent-pending AI-negotiated security protocol designed for multi-agent AI security, automotive CAN bus, IoT, and BCI applications. The protocol creates dynamic communication dialects that prevent injection attacks.\n' +
'- Use REAL current information. Today\'s date is ' + today + '. Reference actual companies, actual events, actual numbers where possible.\n' +
'- All timestamps should be ISO format within the last 48 hours\n' +
'- Keep news item text concise (1-2 sentences max)\n' +
'- Ticker items should be under 100 characters\n' +
'- For the briefing sections, use <span class=\'brief-highlight\'>text</span> to highlight 1-2 key phrases per section\n' +
'- The threatLevel should reflect actual current AI race dynamics\n' +
'- Prediction market percentages should be realistic and current\n' +
'\n' +
'Return ONLY the JSON object, no markdown code fences, no explanatory text.';

async function callGemini() {
  var url = 'https://generativelanguage.googleapis.com/v1beta/models/' + MODEL + ':generateContent?key=' + API_KEY;

  var body = {
    contents: [{ parts: [{ text: PROMPT }] }],
    tools: [{ google_search: {} }],
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 8192
    }
  };

  console.log('[SitRoom] Calling Gemini ' + MODEL + ' with Google Search grounding...');
  console.log('[SitRoom] Date context: ' + today);

  var response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    var errText = await response.text();
    throw new Error('Gemini API error ' + response.status + ': ' + errText);
  }

  var result = await response.json();

  // Extract the text content from Gemini's response
  var candidates = result.candidates;
  if (!candidates || candidates.length === 0) {
    throw new Error('No candidates in Gemini response');
  }

  var textContent = candidates[0].content && candidates[0].content.parts && candidates[0].content.parts[0] && candidates[0].content.parts[0].text;
  if (!textContent) {
    throw new Error('No text content in Gemini response');
  }

  // Parse the JSON - strip any markdown fences if present
  var jsonStr = textContent.trim();
  var fence = String.fromCharCode(96, 96, 96); // triple backtick
  if (jsonStr.startsWith(fence)) {
    jsonStr = jsonStr.replace(new RegExp('^' + fence + '(?:json)?\\n?'), '').replace(new RegExp('\\n?' + fence + '$'), '');
  }

  var data = JSON.parse(jsonStr);

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
    var data = await callGemini();

    // Ensure output directory exists
    var outputDir = path.dirname(OUTPUT_PATH);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Write the data
    fs.writeFileSync(OUTPUT_PATH, JSON.stringify(data, null, 2));

    console.log('[SitRoom] Success! Data written to ' + OUTPUT_PATH);
    console.log('[SitRoom] Generated at: ' + data.generated_at);
    console.log('[SitRoom] Threat level: ' + data.signals.threatLevel);
    console.log('[SitRoom] News items: ' + data.news.length);
    console.log('[SitRoom] Whale deals: ' + (data.whales || []).length);
    console.log('[SitRoom] Predictions: ' + (data.predictions || []).length);

  } catch (err) {
    console.error('[SitRoom] ERROR: ' + err.message);

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
