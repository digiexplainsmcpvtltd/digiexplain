# Digi AI Portal - AI Chat Setup

The dashboard chat now calls the server-side Vercel function at /api/chat. The OpenAI secret is never placed in browser JavaScript.

## Configure
1. Import this GitHub repository into Vercel, or use the existing connected Vercel project.
2. In Vercel Project Settings > Environment Variables, add OPENAI_API_KEY with your OpenAI API key.
3. Optionally add OPENAI_MODEL. Default: gpt-4.1-mini.
4. Redeploy the project.
5. Open digi-ai/dashboard.html on the deployed site and test the AI Assistant card.

Never put the API key in dashboard.html or commit it to GitHub.

## Current boundaries
- AI chat endpoint is implemented but requires OPENAI_API_KEY and deployment.
- Chat history currently remains in browser memory for the current page session.
- Web portal cannot directly read laptop files. The local desktop companion must be running and securely paired before laptop access can be enabled.
- WhatsApp, email, Urdu speech-to-speech, CRM/finance live data and desktop control are not connected yet; they require separate authorization and implementation.
- Add authenticated user sessions and rate limiting before public launch.