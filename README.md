# DEX Swapper

**Operator dashboard for MEV-protected DNX⇄USDC swaps on Ethereum — preset buttons, live quotes, bundle submission to multiple builders, and recovery tooling when nonces stick.**

**DEX Swapper** is a self-hosted FastAPI workstation for **Wrapped Dynex (0xDNX) ↔ USDC** on Ethereum mainnet. One page covers sell and buy swap grids, USDC and ETH sends to saved exchange addresses, live MEXC price ticks, wallet balances, and utilities for stuck transactions — all swaps route through **MEV bundles** (no public mempool fallback) with optional Flashbots Fast cancel capped at a small USD fee.

Built for **operators who need fast, repeatable DNX desk swaps** with gas tiers from JSON config and manual GWEI override. Wallet keys stay in local `.env`; this overview describes product behaviour only.

**Made by [Logic Encoder](https://logicencoder.com)**

Private source: [logicencoder/dex-swapper](https://github.com/logicencoder/dex-swapper)

---

## What you can do

| Area | In plain language |
|------|-------------------|
| **Sell DNX → USDC** | Sixteen preset amounts (1K–25K DNX) with Config Gas tiers or Custom GWEI |
| **Buy DNX ← USDC** | Fifteen USDC presets plus **ALL** balance; Config or Custom gas |
| **Live quotes** | Poll expected out, min after slippage, MEXC reference — chain truth for minReturn |
| **Send USDC** | Address book, MEXC/Gate presets, partial or full balance via MEV path |
| **Send ETH** | Outbound ETH transfer (not a swap) — gas asset only |
| **MEV bundles** | Parallel blast to BeaverBuild and Titan across upcoming blocks |
| **Cancel swap** | Replace pending swap via Flashbots Fast within ~$5 fee cap |
| **Recovery** | Check stuck txs, cancel specific nonce, cancel all pending |
| **Node health** | Switch Infura/Alchemy/local Geth; compare sync and latency |
| **Live logs** | WebSocket stream of blocks, prices, balances, swap status |

---

## Feature examples (two per capability)

#### Sell DNX → USDC (Config Gas)
1. You click **Config Gas “4K”** — sells 4000 DNX using the matching tier from `dex_swapper_gas_config.json`.
2. Bundle blast submits to multiple builders; the live log shows accept timing and mined hash.

#### Sell DNX → USDC (Custom Gas)
1. You enter 8000 DNX and **Custom** 3.0 GWEI — JSON tiers are bypassed for this swap.
2. If the on-chain quote fails, the swap is blocked — MEXC price is display-only, not minReturn.

#### Buy DNX ← USDC
1. You click **500 USDC** Config Gas — buys DNX via 1inch `unoswap2` route constants.
2. You click **ALL** with custom gas — sends full USDC balance with your manual priority fee.

#### On-chain quoting and slippage
1. The UI polls swap quote every few seconds showing expected out and min after your slippage percent.
2. Settings save slippage 2% — minReturn recalculates on the next quote refresh.

#### Send USDC to exchange
1. You select **MEXC Exchange**, preset **500 USDC**, Config send — ERC20 transfer via MEV bundles.
2. **MEXC — All Balance** sends entire USDC to the deposit address from your address book.

#### Send ETH (transfer only)
1. You expand **Send ETH**, send **0.5 ETH** to a saved Gate.io address with Config gas.
2. **All Balance (minus gas)** drains spendable ETH after reserving the gas estimate.

#### MEV bundle submission
1. A swap confirms when Titan accepts the bundle for block N+1 within the wait window.
2. Both builders error — swap fails immediately with no mempool fallback; cancel banner clears.

#### MEV connection keep-alive
1. Long idle session — periodic `eth_chainId` pings keep builder TCP sessions warm for fast blast latency.
2. One builder fails init — it is excluded; the app continues with fewer builders.

#### Auto re-blast
1. Bundle accepted but tx not visible for ~24s — automatic re-blast with the same signed raw tx.
2. After many re-blast attempts, monitoring continues until timeout; balances refresh on abort.

#### Cancel current swap
1. Swap in flight — you hit **Cancel** — self-tx via Flashbots Fast capped at ~$5; monitor aborts wait on receipt.
2. Cancel not feasible when original fees exceed the budget — API returns not feasible.

#### Attacker block monitor
1. A known hardcoded attacker address sends a tx in a new block — cancel-all pending fires automatically.
2. Normal blocks update base fee and block number only — no cancel triggered.

#### Nonce management
1. Rapid sequential swaps use internal nonce counter when pending count exceeds chain latest.
2. Nonce diagnostics show gap between pending and latest for wallet desync debugging.

#### Stuck transaction detection
1. **Check Stuck** scans recent blocks and populates pending list with nonce and gas params.
2. No stuck txs — utilities panel shows green confirmation.

#### Cancel all and cancel specific nonce
1. Two pending nonces after a failed session — **Cancel ALL** Flashbots-cancels each sequentially.
2. Settings: cancel nonce at 30 GWEI — MEV bundle self-tx replaces the stuck slot.

#### Node provider switching
1. You switch to Infura with API key in `.env` — HTTP and WS rewire without restart.
2. **Check** on local node compares block height to a public RPC and reports stale block age.

#### Live price feeds
1. MEXC WS pushes DNX tick up — header price flashes green when flash animation is enabled.
2. Feed stale beyond threshold — MEXC ref in quote shows n/a but swap still uses chain quote.

#### Gas tier configuration
1. Sell 20,001 DNX matches a high-tier priority fee and base multiplier from JSON.
2. Missing gas config file — fallback GWEI priority applies for all amounts.

#### Real-time dashboard WebSocket
1. Browser connects to logs WS — receives block, price, balance, and swap_status messages.
2. Swap starts — `in_progress` shows cancel banner; ends on confirm, fail, or cancel.

#### Address book
1. You add “Binance” + address — it persists to config and appears in send dropdowns.
2. You delete an entry — it is removed from JSON and dropdowns on reload.

#### UI and config hot reload
1. You edit box order in `ui_config.json` and hit **Reload Config** — collapse order updates without Python restart.
2. Settings modal saves quote refresh interval — `ui_defaults` updates via API.

---

## What it does not do

- **Not** multi-pair trading UI — DNX ⇄ USDC only on the swap panels (ETH is send-only)
- **Not** production-hardened — README marks experimental / semi-working paths
- **Not** a retail mobile app — operator desk with hot wallet in `.env`
- **Not** CEX order placement — MEXC is price reference only

Wallet keys, gas config, and address book stay local — not published in this overview repo.

---

## Tech stack

| Layer | Technologies |
|-------|----------------|
| Runtime | Python 3.10+, FastAPI, Uvicorn |
| Blockchain | Web3.py, eth-account, eth-abi |
| DEX routing | 1inch AggregationRouter v6 `unoswap2` |
| MEV | BeaverBuild, Titan `eth_sendBundle`; Flashbots Fast for cancel |
| Prices | MEXC REST + protobuf WebSocket |
| Frontend | Inline HTML/CSS/JS in single app module |
| Config | `ui_config.json`, `dex_swapper_gas_config.json`, `.env` |

---

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # PRIVATE_KEY, ACCOUNT_ADDRESS, optional RPC keys
python3 dex_swapper.py   # default http://localhost:8024
```

Requires Ethereum RPC and funded wallet. See the private repo README and [REPOS.md](REPOS.md).

---

## Related repositories

| Repository | Role |
|------------|------|
| [dex-swapper](https://github.com/logicencoder/dex-swapper) | Private application code |
| [dex-swapper-overview](https://github.com/logicencoder/dex-swapper-overview) | This product overview |
| [cex-dex-arb-overview](https://github.com/logicencoder/cex-dex-arb-overview) | Full UniV3 ↔ CEX arbitrage workstation |

See [REPOS.md](REPOS.md).

---

**Made by [Logic Encoder](https://logicencoder.com)** · [GitHub](https://github.com/logicencoder) · [Contact](https://logicencoder.com/contact/)
