# Zeham

An AI agent that watches Mantle Network smart contract events in real time, detects anomalies using on-chain data, and streams security alerts to Telegram and Discord. All agent decisions recorded on-chain via ERC-8004.

## Tech Layers


- Blockchain	Mantle Network (EVM L2) — testnet for dev, mainnet for submission
- Smart contracts	Solidity + Hardhat — ERC-8004 agent identity contract + decision logger
- Chain interaction	ethers.js v6 — subscribe to events, send transactions, read contract state
- Backend runtime	Node.js — event listener process + cron job + REST API
- AI inference	Elfa AI API (primary) + AltLLM (fallback) — apply for free credits
- On-chain data	Nansen API — wallet labels, smart money tracking, entity tags
- Database	PostgreSQL — raw events, alert history, agent decisions
- Alert delivery	node-telegram-bot-api + Discord webhook
- Frontend	Next.js 14 + Tailwind — dashboard UI (App Router)
- Real-time UI	WebSocket or Server-Sent Events — live alert feed
- Deployment	DigitalOcean (you have credentials) — Docker container for backend + Vercel for frontend
- Environment	.env — RPC URL, Nansen key, Elfa key, Telegram token, Discord webhook, private key