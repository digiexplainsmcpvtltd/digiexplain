export default async function handler(req, res) {
  if (req.method !== "POST") { res.setHeader("Allow", "POST"); return res.status(405).json({ error: "Method not allowed" }); }
  const key = process.env.OPENAI_API_KEY;
  if (!key) return res.status(503).json({ error: "OpenAI key is not configured. Add OPENAI_API_KEY in Vercel Environment Variables and redeploy." });
  try {
    const messages = Array.isArray(req.body && req.body.messages) ? req.body.messages : [];
    const input = messages.filter(m => m && ["user", "assistant"].includes(m.role) && typeof m.content === "string").slice(-12).map(m => ({ role: m.role, content: [{ type: "input_text", text: m.content.slice(0, 6000) }] }));
    if (!input.length || messages[messages.length - 1].role !== "user") return res.status(400).json({ error: "Send a user message first." });
    const model = process.env.OPENAI_MODEL || "gpt-4.1-mini";
    const instructions = "You are Digi AI for Digi Explain (SMC-Private) Limited in Pakistan. The company works in printing, packaging, branding, signage, corporate gifts, events, installations and digital marketing. Reply in Roman Urdu, Urdu or English matching the user. Be practical and honest. Never claim access to laptop files, WhatsApp, email or other systems unless an authorized integration supplied that data. Never send messages, publish, spend money or delete files without owner approval.";
    const upstream = await fetch("https://api.openai.com/v1/responses", { method: "POST", headers: { "Authorization": "Bearer " + key, "Content-Type": "application/json" }, body: JSON.stringify({ model, instructions, input, max_output_tokens: 900 }) });
    const data = await upstream.json();
    if (!upstream.ok) return res.status(upstream.status).json({ error: data.error && data.error.message ? data.error.message : "OpenAI request failed." });
    const reply = (data.output || []).flatMap(x => x.content || []).filter(x => x.type === "output_text").map(x => x.text).join("\n");
    if (!reply) return res.status(502).json({ error: "AI returned an empty response." });
    return res.status(200).json({ reply, model });
  } catch (e) { return res.status(500).json({ error: "Server error contacting AI." }); }
}