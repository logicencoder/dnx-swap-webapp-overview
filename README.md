# DEX Swapper

![DEX Swapper — operator dashboard](assets/dex-swapper-featured.png)

Operator-focused **DEX swap console** — today tuned for **Dynex (DNX) on Ethereum**, with preset sell and buy ladders, config-driven gas, live 1inch quotes, MEV builder submission, fund transfers to exchange addresses, and recovery tooling when nonces or mempools misbehave. One browser page replaces juggling wallet pop-ups, spreadsheets, and SSH log tails during active sessions. Additional token pairs can be wired in later without changing the operator workflow.

**Typical flows:** ladder out DNX after a CEX move → tap a **CONFIG GAS** sell size → confirm **Config** with live quote visible → watch **Live Logs** for builder blast and confirmation. Buy the dip → **Buy DNX ← USDC** preset → **Custom** with manual priority fee when the mempool spikes. Move proceeds to MEXC → expand **Send USDC**, pick exchange from the dropdown, **Send (Config)**. Stuck pending swap → **Settings** → **Check Stuck Transactions** → **Cancel Specific Nonce** or **Cancel ALL Pending**. Gas table tweak → edit `dex_swapper_gas_config.json` → **Reload Config** in settings.

## Tech stack

| Layer | Technologies |
|-------|--------------|
| Backend | Python 3, FastAPI, uvicorn, asyncio |
| Chain | Web3.py — swaps via 1inch router, ERC-20 transfers, EIP-1559 gas |
| Pricing | MEXC protobuf WebSocket trades + on-chain pool math for DNX reference |
| Block head | `newHeads` WebSocket — base fee cached in RAM between swaps |
| MEV | HTTP keep-alive to private builders (BeaverBuild, Titan); multi-block bundle blast |
| UI | Single-page HTML/CSS/JS embedded in FastAPI — dark operator theme |
| Streaming | WebSocket `/ws/logs` — structured log, block, price, balance, swap events |
| Config | JSON gas ranges (`dex_swapper_gas_config.json`), UI presets (`ui_config.json`) |
| Secrets | Local `.env` — RPC URLs, private key, builder endpoints (private repo only) |

## Header — chain context and wallet

The top band stays visible while you work the swap cards below.

| Element | Role |
|---------|------|
| **Clock** | Local session time |
| **Block** | Latest head from the block monitor |
| **ETH price** | Reference USD for fee estimates (flash icon when the quote tick updates) |
| **DNX price** | MEXC trade tape + on-chain reference; direction arrow on change |
| **Wallet card** | Truncated address with **ETH**, **DNX**, and **USDC** balances (USD sublabels) |

Balances refresh on a short interval so you see spendable amounts before hitting a preset. **Settings** (gear) opens the modal documented below.

## Sell DNX → USDC and Buy DNX ← USDC

Two side-by-side cards mirror how operators run repeated size ladders.

### Preset grids

Each card exposes two button grids:

| Grid | Behavior |
|------|----------|
| **CONFIG GAS** (purple) | Amount presets from `ui_config.json`; priority fee and base-fee multiplier come from `dex_swapper_gas_config.json` for that size band |
| **CUSTOM GAS** (pink) | Same amount presets; you type priority fee (GWEI) in the **Gas** field and submit with **Custom** |

**Sell DNX** presets span ladder sizes from small clips through large clips (configurable list). **Buy DNX** presets cover USDC notionals plus an **ALL** button that uses full USDC balance rounded down to avoid dust failures.

### Amount, gas, and submit

- **Amount** — numeric field; clicking a preset fills it.
- **Gas** — priority fee in GWEI for custom path; config path ignores manual entry.
- **Config / Custom** — primary actions; each path uses fixed gas limits tuned per operation type (DNX sell, USDC buy, sends).

### Live quote panel

Below each card, a **LIVE QUOTE** box polls the 1inch route (Uniswap V2 path in the UI label). It shows **You receive**, **Min after slip** (slippage from settings), and **MEXC ref** so you can compare on-chain output against the CEX tape before sending. Quotes auto-refresh every 1–60 seconds (configured in settings) without flashing the whole page.

**Estimated cost** under the sell card summarizes expected gas in ETH and USD for the chosen size.

## Send USDC and Send ETH

Collapsible panels below the swap cards move proceeds without leaving the app.

### Send USDC

- **To** — dropdown: named exchange addresses (e.g. MEXC, Gate.io) from the address book, or custom entries you maintain.
- **Amount** — preset chips (including **All Balance**) plus numeric field.
- **Gas** — config or custom priority fee; **Send (Config)** / **Send (Custom)** mirror the swap card pattern.

### Send ETH

Same layout for native ETH transfers — gas presets tuned for smaller limits than swaps. Collapsed by default in the panel order; expand when bridging gas to an exchange wallet.

## Address book

Collapsible **Address Book** panel lists named withdrawal targets (exchanges and custom labels). Entries feed the **Send USDC** / **Send ETH** dropdowns. Add, edit, and persist labels through the UI — no hard-coded-only workflow.

## Utilities panel

Collapsible **Utilities** groups operational shortcuts (nonce inspection, config reload triggers accessible from the main settings modal as well). Use when you need chain hygiene without opening a separate script.

## Settings modal

![Settings — gas defaults, cancel nonce, utilities](assets/dex-swapper-settings.png)

Open via the header gear. Sections:

### Default gas (GWEI)

| Field | Purpose |
|-------|---------|
| **Swap Gas** | Default priority fee for swap submissions |
| **Send Gas** | Default for USDC/ETH sends |
| **Cancel Gas** | Priority for cancel transactions |
| **Slippage %** | `minReturn` tolerance on 1inch quotes |
| **Quote refresh (sec)** | Live quote polling interval (1–60) |

**Save Settings** writes defaults back to `ui_config.json`.

### Cancel specific nonce

Enter **Nonce #** and gas GWEI (minimum ~10% above the original transaction). **Cancel** fires an on-chain cancel through the MEV builder path with a cost ceiling guard.

### Utilities buttons

| Action | Effect |
|--------|--------|
| **Check Stuck Transactions** | Scans pending nonces across a wide block window; lists mempool vs confirmed state **without** auto-cancel |
| **Cancel ALL Pending Transactions** | Broadcasts cancels for every tracked pending nonce via builders |
| **Reload Config** | Re-reads `dex_swapper_gas_config.json` and `ui_config.json` without restarting the process |

## Live logs and MEV submission

The **Live Logs** panel streams color-coded events over WebSocket: gas decisions, quote refreshes, balance updates, block ticks, swap lifecycle, and builder traffic.

On submit, the engine blasts signed raw transactions to connected **MEV builders** across multiple future block targets. Logs show per-builder accept/reject, bundle counts, and latency. When a transaction drops from mempool view, an automatic re-blast can resubmit to builders. Keep-alive pings maintain builder HTTP sessions between trades.

Use this panel instead of tailing server stdout during time-sensitive sells.

## Node and RPC selection

**Node settings** (collapsible panel) switch between **local Geth**, **Infura**, **Alchemy**, and **QuickNode** profiles defined in `ui_config.json`. Health check and test actions confirm HTTP/WS reachability before you route production size. Chain ID stays on Ethereum mainnet.

## Recovery and safety

Built for operational incidents, not unattended bots:

- **Cancel current swap** — targets the nonce assigned to the in-flight swap.
- **Cancel current send** — same for the active USDC/ETH send.
- **Nonce status API** — compares blockchain pending vs locally tracked nonce (helps when an external wallet desyncs).
- **Stuck scan** — deep block walk for your address’s transactions per nonce.
- **Cancel all** — emergency clear of the pending map.

Treat elevated cancel gas and builder cancel paths as operator-grade tools — test on small size before relying on them under load.

## Configuration files

| File | Role |
|------|------|
| `dex_swapper_gas_config.json` | Amount bands → priority fee + base-fee multiplier for config-gas path |
| `ui_config.json` | Preset ladders, panel collapse order, address book, node profiles, UI defaults |
| `.env` | Private key, API keys, optional builder URLs — **private repo only** |

## Quick start

```bash
# private repo — configure .env and gas JSON first
python3 dex_swapper.py
```

Default browser URL uses the port in `ui_config.json` (commonly `8024` in development).

Private implementation: [logicencoder/dex-swapper](https://github.com/logicencoder/dex-swapper).

See [REPOS.md](REPOS.md) for repository links.

---

**Made by [Logic Encoder](https://logicencoder.com)** · [GitHub](https://github.com/logicencoder) · [Contact](https://logicencoder.com/contact/)
