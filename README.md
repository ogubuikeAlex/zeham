<div align="center">

<img src="https://img.shields.io/badge/Mantle_Network-EVM_L2-00C2CB?style=for-the-badge&logo=ethereum&logoColor=white" />
<img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" />
<img src="https://img.shields.io/badge/Solidity-0.8.20-363636?style=for-the-badge&logo=solidity&logoColor=white" />
<img src="https://img.shields.io/badge/ERC--8004-Agent_Identity-8B5CF6?style=for-the-badge" />

<br />
<br />

```
███████╗███████╗██╗  ██╗ █████╗ ███╗   ███╗
╚══███╔╝██╔════╝██║  ██║██╔══██╗████╗ ████║
  ███╔╝ █████╗  ███████║███████║██╔████╔██║
 ███╔╝  ██╔══╝  ██╔══██║██╔══██║██║╚██╔╝██║
███████╗███████╗██║  ██║██║  ██║██║ ╚═╝ ██║
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
```
</div>
<div align="center">

### AI-Powered On-Chain Security Monitor for Mantle Network

**Real-time anomaly detection · On-chain agent identity (ERC-8004) · Instant alerts**

<br />

[Live Dashboard](https://zeham-fe.vercel.app/) · [API Docs](https://zeham-backend.onrender.com/docs) · [Mantle Explorer](https://explorer.mantle.xyz) · [Demo Video](#demo)

<br />


> Built for the **Mantle Turing Test Hackathon 2026** Track 2 -> AI Alpha & Data

</div>

---

## What is zeham?

zeham is an autonomous AI security agent that monitors smart contracts on the Mantle Network in real time. It detects anomalies like, flash loan attacks, rug pulls, whale moves, wash trading, and contract exploits, the moment they happen, sends instant alerts to Telegram and Discord, and records every agent decision permanently on the Mantle blockchain via the ERC-8004 agent identity standard.

Think of it as a SIEM (Security Information and Event Management) system, but purpose-built for on-chain DeFi security.

**The core loop runs every 60 seconds:**

```
Mantle on-chain events
        ↓
  Event Listener (web3.py WebSocket)
        ↓
  Nansen API enrichment (wallet labels)
        ↓
  Rule Engine (5 detection classes)
        ↓
  AI Inference (Elfa AI → AltLLM fallback)
        ↓
  ERC-8004 on-chain decision log (Mantle)
        ↓
  Telegram + Discord alerts + Live Dashboard
```

---

## Features

### Real-Time Event Ingestion
- Subscribes to Mantle smart contract events via WebSocket RPC
- Captures Transfer, Swap, Mint, Burn, Liquidation, and unknown call patterns
- Enriches every event with Nansen wallet intelligence labels (smart money, known exploiter, whale, mixer)
- Stores enriched events to PostgreSQL within 5 seconds of on-chain emission
- Supports runtime contract registration via API or Telegram `/watch` command — no restart needed

### Two-Layer AI Detection Engine
- **Layer 1 — Rule Engine:** Five deterministic detection classes that fire instantly without API cost
  - Flash Loan Attack detection (multi-event-type in single tx + flash loan signatures)
  - Rug Pull / Liquidity Drain (high concentration of removals from one wallet)
  - Whale Move (high-frequency large transfers, cross-referenced with Nansen labels)
  - Wash Trading (same wallet on both sides of repeated swaps)
  - Contract Exploit (known exploiter Nansen labels + unusual call pattern spikes)
- **Layer 2 — AI Inference:** Elfa AI (primary) with AltLLM as automatic fallback
  - Structured JSON-only prompts — no free-form AI hallucination in alert output
  - Returns severity, anomaly type, confidence score, and recommended action
  - Fallback chain: Elfa AI → AltLLM → rule-only alerts (system never goes dark)

### ERC-8004 On-Chain Agent Identity
- Every agent decision includingr anomaly or clean scan, is logged permanently on Mantle
- `logDecision(anomalyType, severity, reason, contractTarget, isAnomaly)` called after every cycle
- `DecisionLogged` events are queryable on the Mantle block explorer without calling the contract
- Full audit trail: judges, operators, and users can verify every detection decision on-chain
- Contract is `Ownable` meaning only the zeham agent wallet can write decisions

### 📢 Instant Multi-Channel Alerts
- CRITICAL and HIGH alerts sent immediately (within 10 seconds of detection)
- MEDIUM and LOW alerts batched into a digest every 10 minutes (prevents notification fatigue)
- Deduplication: same contract + anomaly type pair suppressed within 10-minute window
- Telegram: formatted HTML cards with severity badge, contract link, confidence score, Mantle explorer link
- Discord: colour-coded embeds (red = CRITICAL, orange = HIGH, yellow = MEDIUM)
- Browser notifications: CRITICAL alerts flash the page title and trigger a browser push notification

### 📊 Live Dashboard
- **Home:** Real-time alert feed via WebSocket — new alerts slide in without page refresh
- **Heatmap:** Alert volume grid by contract address (rows) × hour of day (columns)
- **Agent Log:** Full audit trail of every AI detection cycle with expandable prompt and response
- **Watch:** Add contracts to monitor via a validated form. No Telegram command required
- Stats bar: alerts today, critical count, contracts monitored, total on-chain decisions

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           zeham System                                      │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        FastAPI Backend (Render)                      │   │
│  │                                                                      │   │
│  │  ┌────────────────┐  ┌───────────────┐  ┌────────────────────────┐  │    │
│  │  │ EventListener  │  │ DetectionEngine│  │  AlertBroadcaster      │  │   │
│  │  │                │  │               │  │                        │  │    │
│  │  │ web3.py WS     │  │ Rule Engine   │  │ Polls every 10s        │  │    │
│  │  │ Mantle RPC     │  │ +             │  │ Telegram bot           │  │    │
│  │  │ Nansen enrich  │  │ Elfa AI       │  │ Discord webhook        │  │  │
│  │  │ Postgres write │  │ AltLLM        │  │ WS broadcast           │  │  │
│  │  └───────┬────────┘  └──────┬────────┘  └────────────────────────┘  │  │
│  │          │                  │                                         │  │
│  └──────────┼──────────────────┼─────────────────────────────────────── ┘  │
│             │                  │                                             │
│             ▼                  ▼                                             │
│  ┌─────────────────┐  ┌─────────────────────────────────────────────────┐  │
│  │   Supabase      │  │           Mantle Network (EVM L2)                │  │
│  │   PostgreSQL    │  │                                                  │  │
│  │                 │  │  MantisAgentIdentity.sol (ERC-8004)              │  │
│  │  events         │  │  logDecision() ← called every detection cycle   │  │
│  │  alerts         │  │  DecisionLogged event → queryable on explorer   │  │
│  │  detection_logs │  │                                                  │  │
│  │  watched_contr. │  └─────────────────────────────────────────────────┘  │
│  └─────────────────┘                                                        │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    Next.js Dashboard (Vercel)                        │  │
│  │                                                                      │  │
│  │   / Alert Feed  │  /heatmap  │  /agent Log  │  /watch Manager       │  │
│  │   WebSocket ────────────────────────────────────────────────────▶   │  │
│  │   Real-time alerts push                                              │  │
│  └──────────────────────────────────────────────────────────────────── ┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Blockchain | Mantle Network (EVM L2) | Target chain — all contracts monitored here |
| Smart Contract | Solidity 0.8.20 + Hardhat | ERC-8004 agent identity contract |
| Backend Runtime | Python 3.12 + FastAPI | Event listener, detection engine, alert broadcaster |
| Chain Interaction | web3.py v7 | WebSocket event subscription, contract calls |
| AI Inference | Elfa AI + AltLLM | Anomaly classification with fallback chain |
| On-Chain Data | Nansen API | Wallet labels, smart money intelligence |
| Scheduler | APScheduler | 60s detection cycles, 10s broadcaster cycles |
| Database | PostgreSQL via SQLAlchemy + asyncpg | Event storage, alert history, agent logs |
| Hosted DB | Supabase | Managed Postgres with SSL, free tier |
| Alert Delivery | python-telegram-bot + Discord webhooks | Real-time operator notifications |
| Frontend | Next.js 14 (App Router) + TypeScript | Live dashboard, SSR first paint |
| Charting | Recharts | Severity heatmap, trend visualisations |
| Styling | Tailwind CSS | Utility-first, dark theme |
| Backend Hosting | Render | Python web service, WebSocket support |
| Frontend Hosting | Vercel | Edge-optimised Next.js deployment |

---

## Repository Structure

```
zeham/
│
├── render.yaml                          # Render deployment config (read from repo root)
├── .gitignore
│
├── contracts/                           # Hardhat — Solidity smart contracts
│   ├── contracts/
│   │   ├── MantisAgentIdentity.sol      # ERC-8004 agent identity contract
│   │   └── FlashLoanSimulator.sol       # Test contract for triggering detection
│   ├── scripts/
│   │   ├── deploy.js                    # Deploy to Mantle testnet
│   │   ├── deploy-mainnet.js            # Deploy to Mantle mainnet
│   │   └── verify-args.js              # Constructor args for contract verification
│   ├── test/
│   │   └── MantisAgentIdentity.test.js  # 7 Hardhat tests
│   ├── abis/
│   │   └── MantisAgentIdentity.json     # ABI exported after compile
│   ├── hardhat.config.js
│   └── package.json
│
├── backend/                             # FastAPI — Python backend
│   ├── main.py                          # App bootstrap, startup, WebSocket endpoint
│   ├── config.py                        # Pydantic settings — all env vars
│   ├── scheduler.py                     # APScheduler — wires detection + broadcaster cycles
│   │
│   ├── listener/                        # ADR-001: Event ingestion
│   │   ├── event_listener.py            # WebSocket connection + event subscription
│   │   ├── decoder.py                   # ABI decoding for known event signatures
│   │   └── reconnect.py                 # Exponential backoff reconnection
│   │
│   ├── nansen/                          # Nansen API client
│   │   ├── client.py                    # Async wallet label enrichment
│   │   └── models.py                    # Pydantic response models
│   │
│   ├── db/                              # Database layer
│   │   ├── database.py                  # SQLAlchemy async engine + session factory
│   │   ├── models.py                    # ORM table definitions
│   │   └── repository.py               # EventRepository: insert + update methods
│   │
│   ├── agent/                           # ADR-002: AI detection engine
│   │   ├── engine.py                    # Main orchestrator — runs the 60s cycle
│   │   ├── fetcher.py                   # Queries unprocessed events from DB
│   │   ├── writer.py                    # AlertWriter: DB + ERC-8004 on-chain log
│   │   ├── rules/                       # Rule-based detection (Layer 1)
│   │   │   ├── base.py                  # BaseRule abstract class + RuleAlert dataclass
│   │   │   ├── flash_loan.py            # Flash loan attack detection
│   │   │   ├── rug_pull.py              # Rug pull / liquidity drain detection
│   │   │   ├── whale.py                 # Whale accumulation / dump detection
│   │   │   ├── wash_trade.py            # Wash trading detection
│   │   │   └── exploit.py              # Contract exploit / unusual call pattern
│   │   └── ai/                          # AI inference (Layer 2)
│   │       ├── elfa_client.py           # Elfa AI API client (primary)
│   │       ├── altllm_client.py         # AltLLM API client (fallback)
│   │       ├── prompt.py                # System prompt + user prompt builder
│   │       └── parser.py               # AI JSON response validator
│   │
│   ├── broadcaster/                     # ADR-003: Alert delivery
│   │   ├── broadcaster.py               # Main broadcaster — 10s poll cycle
│   │   ├── telegram_notifier.py         # Telegram bot message builder + sender
│   │   ├── discord_notifier.py          # Discord webhook embed builder + sender
│   │   ├── telegram_commands.py         # /watch /status /help bot commands
│   │   ├── deduplicator.py              # Suppress duplicate alerts within 10min window
│   │   ├── digest.py                    # MEDIUM/LOW batch digest buffer
│   │   └── formatter.py                # Alert → human-readable Telegram HTML + Discord embed
│   │
│   ├── api/                             # FastAPI route handlers
│   │   ├── alerts.py                    # GET /alerts, GET /alerts/stats
│   │   ├── agent.py                     # GET /agent/log, GET /agent/identity
│   │   ├── watch.py                     # POST /watch, GET /health
│   │   ├── contracts.py                 # GET /contracts
│   │   ├── heatmap.py                   # GET /heatmap
│   │   └── subscriptions.py            # POST /subscribe, GET /subscriptions
│   │
│   ├── ws/
│   │   └── connection_manager.py        # WebSocket broadcast manager
│   │
│   ├── abis/
│   │   └── MantisAgentIdentity.json     # Copied from contracts/abis/ after compile
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env                             # Local only — never committed
│
└── frontend/                            # Next.js 14 — dashboard
    ├── app/
    │   ├── layout.tsx                   # Root layout — Navbar, SWR config, theme
    │   ├── page.tsx                     # / — Live Alert Feed
    │   ├── agent/page.tsx               # /agent — Agent Decision Log
    │   ├── watch/page.tsx               # /watch — Contract Watchlist Manager
    │   └── heatmap/page.tsx             # /heatmap — Severity Heatmap
    │
    ├── components/
    │   ├── shared/                      # Navbar, SeverityBadge, AddressDisplay, etc.
    │   ├── home/                        # AlertFeed, AlertCard, StatsBar, FilterBar
    │   ├── agent/                       # AgentIdentityCard, DecisionLogTable
    │   ├── watch/                       # AddContractForm, WatchedContractsTable
    │   └── heatmap/                     # SeverityHeatmap, TopOffendersTable
    │
    ├── hooks/
    │   ├── useWebSocket.ts              # Custom hook — WS connection state machine
    │   └── useInterval.ts              # Live relative timestamp updates
    │
    ├── types/index.ts                   # TypeScript interfaces for all API responses
    ├── lib/
    │   ├── api.ts                       # Typed fetch wrappers
    │   ├── swr-config.ts               # Global SWR options
    │   └── formatters.ts               # Address truncation, severity labels, time formatting
    │
    ├── vercel.json
    ├── next.config.js
    └── .env.local                       # Local only — never committed
```

---

## Detection Rules

zeham detects five classes of on-chain anomaly. Every rule is a Python class that evaluates a batch of events for one contract in one 60-second window.

| Rule | Anomaly Type | Severity | Detection Logic |
|---|---|---|---|
| `FlashLoanRule` | `flash_loan` | CRITICAL | Single tx contains 3+ distinct event types AND matches flash loan function signatures OR sender is labelled `known exploiter` by Nansen |
| `RugPullRule` | `rug_pull` | CRITICAL / HIGH | 80%+ of liquidity removal events in one window originate from a single wallet. CRITICAL if Nansen labels that wallet as `deployer` or `team` |
| `WhaleMoveRule` | `whale` | HIGH / MEDIUM / LOW | 5+ events from/to one wallet in 60 seconds. HIGH if wallet is labelled `mixer` or `unknown`. MEDIUM if `smart money`. LOW otherwise |
| `WashTradeRule` | `wash_trade` | MEDIUM | Same wallet address appears as both sender and receiver in 3+ swap events within one window |
| `ContractExploitRule` | `exploit` | CRITICAL / HIGH | CRITICAL if any event sender is labelled `exploiter`, `hacker`, `drainer`, or `scammer` by Nansen. HIGH if 40%+ of events in the window are `Unknown` event type |

When a CRITICAL rule fires, the AI inference call is skipped — the alert is written immediately. This ensures CRITICAL alerts are never delayed by AI API latency.

---

## ERC-8004 Contract

The `MantisAgentIdentity` contract is deployed on Mantle Network and serves as the permanent, tamper-proof audit trail for all zeham agent decisions.

**Contract address (testnet):** `0x85f92f292aF22CE06BBbc76B7DA799955437a82a`
**Network:** Mantle Sepolia Testnet (chainId: 5003)
**Explorer:** [View on Mantle Testnet Explorer](https://explorer.sepolia.mantle.xyz/address/0x85f92f292aF22CE06BBbc76B7DA799955437a82a)

### Key functions

```solidity
// Called by the backend after every detection cycle
function logDecision(
    string calldata anomalyType,    // flash_loan | rug_pull | whale | wash_trade | exploit | none
    string calldata severity,       // CRITICAL | HIGH | MEDIUM | LOW | NONE
    string calldata reason,         // Human-readable explanation
    string calldata contractTarget, // The monitored contract that triggered this decision
    bool isAnomaly                  // true if anomaly detected, false for clean scans
) external onlyOwner

// Query decisions
function getDecision(uint256 index) external view returns (Decision memory)
function getDecisionCount() external view returns (uint256)
function getRecentDecisions(uint256 count) external view returns (Decision[] memory)
function getAgentIdentity() external view returns (name, version, description, agentWallet, deployedAt, decisionCount)
```

Every call to `logDecision` emits a `DecisionLogged` event visible on the block explorer without any contract interaction.

---

## API Reference

The backend exposes a full REST API documented interactively at `/docs` (Swagger UI).

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check + active contract count |
| `GET` | `/alerts` | Paginated alert list. Filter by `severity` and `type` query params |
| `GET` | `/alerts/stats` | Counts: alerts today, critical today, contracts monitored, on-chain decisions |
| `GET` | `/agent/log` | Detection cycle audit log with raw AI prompts and responses |
| `GET` | `/agent/identity` | ERC-8004 agent metadata from the on-chain contract |
| `GET` | `/contracts` | All watched contracts with event counts |
| `POST` | `/watch` | Add a contract to the monitoring list at runtime |
| `GET` | `/heatmap` | Alert volume by contract × hour. Query param: `range=24h\|7d\|30d` |
| `WS` | `/ws/alerts` | WebSocket — pushes new alert objects to connected dashboard clients |

---

## Getting Started

### Prerequisites

- Node.js v18+
- Python 3.12+
- Docker Desktop
- A Mantle testnet wallet with MNT (from [faucet.sepolia.mantle.xyz](https://faucet.sepolia.mantle.xyz))

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/zeham.git
cd zeham
```

### 2. Install contract dependencies and deploy

```bash
cd contracts
npm install
npm run compile
npm run test          # all 7 tests must pass
npm run deploy:testnet
# Copy the deployed address to backend/.env as ERC8004_CONTRACT_ADDRESS
# Copy the ABI: cp abis/MantisAgentIdentity.json ../backend/abis/
```

### 3. Set up the backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create backend/.env — see Environment Variables section below
# Start PostgreSQL:
docker compose up db -d

# Start the backend:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Set up the frontend

```bash
cd frontend
npm install

# Create frontend/.env.local — see Environment Variables section below
npm run dev
# Open http://localhost:3000
```

### 5. Add a contract to watch

```bash
curl -X POST http://localhost:8000/watch \
  -H "Content-Type: application/json" \
  -d '{"address": "0x201eba5cc46d216ce6dc03f6a759e8e766e956ae", "label": "USDT Mantle"}'
```

### 6. Trigger a test alert

```bash
# Inject a synthetic flash loan event pattern
docker exec -it mantis-db psql -U mantis -d zeham -c "
INSERT INTO alerts (contract_address, severity, anomaly_type, reason, confidence, source, source_event_ids, notified, fired_at)
VALUES ('0x201eba5cc46d216ce6dc03f6a759e8e766e956ae', 'CRITICAL', 'flash_loan',
        'Test: flash loan pattern detected.', 0.95, 'RULE',
        ARRAY['00000000-0000-0000-0000-000000000001'], FALSE, NOW());
"
# Watch it appear in your Telegram, Discord, and dashboard within 10 seconds
```

---

## Environment Variables

### Backend (`backend/.env`)

```bash
# Mantle Network
MANTLE_WS_URL=wss://rpc.sepolia.mantle.xyz        # testnet | wss://rpc.mantle.xyz for mainnet
MANTLE_HTTP_URL=https://rpc.sepolia.mantle.xyz

# Agent Wallet
AGENT_PRIVATE_KEY=0xYOUR_PRIVATE_KEY               

# ERC-8004 Contract (fill after deployment)
ERC8004_CONTRACT_ADDRESS=
ERC8004_NETWORK=testnet

# Database (local dev)
DATABASE_URL=postgresql+asyncpg://mantis:mantis@localhost:5432/zeham

# API Integrations (apply for credits at devhub.mantle.xyz)
NANSEN_API_KEY=
NANSEN_BASE_URL=https://api.nansen.ai/v1
ELFA_API_KEY=
ALTLLM_API_KEY=

# Telegram (from BotFather)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=                                  

# Discord (webhook URL from channel settings)
DISCORD_WEBHOOK_URL=

# App
MANTLE_EXPLORER_BASE=https://explorer.sepolia.mantle.xyz
LOG_LEVEL=INFO
```

### Frontend (`frontend/.env.local`)

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/alerts
NEXT_PUBLIC_EXPLORER_BASE=https://explorer.sepolia.mantle.xyz
NEXT_PUBLIC_ERC8004_ADDRESS=                       
```

---

## Deployment

zeham is deployed across three platforms. Configuration files are included in the repo.

| Service | Platform | Config file |
|---|---|---|
| Backend (FastAPI) | [Render](https://render.com) | `render.yaml` at repo root, `rootDir: backend` |
| Frontend (Next.js) | [Vercel](https://vercel.com) | `frontend/vercel.json`, root directory set to `frontend/` in Vercel dashboard |
| Database | [Supabase](https://supabase.com) | Direct connection (port 5432) with `ssl=require` and `NullPool` |
| Smart Contract | Mantle Mainnet | `npm run deploy:mainnet` from `contracts/` |

For the full step-by-step deployment guide including Supabase SSL config, Render secret management, Vercel WebSocket setup, and mainnet contract deployment, see [DEPLOY-zeham.md](./DEPLOY-zeham.md).

For local development and testing, including how to trigger flash loans and run the full alert pipeline, see [RUNBOOK-zeham.md](./RUNBOOK-zeham.md).

---

## Demo

> Demo video: []

The demo shows:

1. zeham dashboard live at the Vercel URL
2. A flash loan simulation transaction sent to Mantle testnet
3. The event captured in the live alert feed within seconds
4. CRITICAL alert appearing in Telegram and Discord
5. The ERC-8004 `DecisionLogged` event visible on the Mantle block explorer
6. The AI prompt and response visible in the Agent Log page

---

## Hackathon Context

| Field | Detail |
|---|---|
| **Hackathon** | Mantle Turing Test Hackathon 2026 |
| **Track** | Track 2 — AI Alpha & Data |
| **Platform** | DoraHacks |
| **Sponsor integrations** | Mantle Network (ERC-8004), Nansen API, Elfa AI, AltLLM |
| **On-chain contract** | `MantisAgentIdentity.sol` — deployed on Mantle mainnet |
| **AI providers** | Elfa AI (primary inference) + AltLLM (fallback) |

---

## Project Documents

| Document | Description |
|---|---|
| [ADR-001](./docs/ADR-001-zeham-EventListener.md) | Blockchain event listener, Nansen enrichment, database design |
| [ADR-002](./docs/ADR-002-zeham-AIDetectionEngine.md) | AI detection engine rules + Elfa AI inference |
| [ADR-003](./docs/ADR-003-zeham-AlertSystem-ERC8004.md) | Alert system using Telegram, Discord, ERC-8004 contract |
| [ADR-004](./docs/ADR-004-zeham-Dashboard-UI.md) | Dashboard UI, pages, components, WebSocket strategy |
| [RUNBOOK](./RUNBOOK-zeham.md) | Local setup, running the app, triggering test alerts |
| [DEPLOY](./DEPLOY-zeham.md) | Production deployment using Render, Vercel, Supabase, Mantle mainnet |
| [design.md](./design.md) | Visual design system with theme, colours, typography |

---

## Acknowledgements

- [Mantle Network](https://mantle.xyz) — the EVM L2 this entire system is built around
- [Nansen](https://nansen.ai) — on-chain wallet intelligence that makes detection meaningful
- [Elfa AI](https://elfa.ai) — AI inference engine for anomaly classification
- [AltLLM](https://altllm.com) — fallback inference provider
- [OpenZeppelin](https://openzeppelin.com) — battle-tested Solidity contracts (Ownable)

---

<div align="center">

Built with 🛡️ for the Mantle ecosystem

**zeham because on-chain security shouldn't require a human watching a terminal.**
