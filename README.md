# DNX Swap WebApp

![DNX Trading UI](assets/ui.png)

Operator-focused trading web application for **Dynex (DNX)** on Ethereum — fast DNX⇄USDC swaps, live balances and prices, config-driven gas, MEV builder submission, and recovery tooling when the chain misbehaves.

Private source: [logicencoder/dnx-swap-webapp](https://github.com/logicencoder/dnx-swap-webapp). Keys, RPC endpoints, and builder secrets stay in your local `.env` — never in this overview repo.

## The problem it solves

Standard DEX UIs spread the workflow across too many screens. Base fee and priority fee move while you type an amount. Nonce desync and stuck pending transactions are routine under active trading. MEV exposure affects whether a swap confirms at the price you assumed.

DNX Swap WebApp is a **single-page operator runtime** — balances, prices, block head, preset sizes, gas modes, and a live log stream on one surface, with separate recovery actions when chain state goes wrong.

## Preset-driven sell and buy

Two cards — **Sell DNX → USDC** and **Buy DNX ← USDC** — with preset amount buttons (16 sell sizes, 15 buy sizes), optional custom amounts, and an **ALL** buy using full USDC balance rounded down to avoid dust failures. One-click sizes for repeated daily ladders during volatile sessions.

## Config and custom gas

Each card supports **Config Gas** (reads amount ranges from `dnx_swap_gas_config.json`) or **Custom Gas** (operator override). JSON maps trade size → priority fee (gwei) and base fee multiplier. Fixed gas limits: DNX sell 310k, USDC buy 280k, USDC send 65k, ETH send 21k.

## Live state without tab switching

Wallet balances (ETH, DNX, USDC) refresh on a short cache interval. Prices combine **MEXC WebSocket** trades (protobuf decode) with on-chain pool math. Current block and base fee come from a **newHeads** WebSocket — base fee cached in RAM without per-tick `get_block` RPC calls.

## WebSocket log stream

Structured events — logs, blocks, prices, balances, swap status — broadcast to the browser over WebSocket so the UI stays the control surface; no SSH tailing during failed swaps or slow confirmations.

## MEV builder path

Persistent HTTP keep-alive to **BeaverBuild** and **Titan**, bundle submission across future block slots, health pings, optional auto-reblast when a transaction drops from the mempool, and periodic builder stats. Public mempool alone is often too slow for the size ladders this UI targets.

## Fund transfers

Send USDC or ETH to preset exchange withdrawal addresses (MEXC, Gate.io) or a custom recipient, with gas limits tuned per asset — for moving proceeds to CEX accounts after on-chain legs.

## Recovery and safety tooling

Dedicated section for operational incidents: cancel current swap, cancel all pending, nonce inspection, stuck-transaction scan across a wide block window, and elevated-gas self-transfers for cancel paths. Block monitor can watch configured addresses and trigger defensive cancels. Treat recovery utilities as operator-grade — harden before unattended automation.

## Configuration

- `dnx_swap_gas_config.json` — gas ranges by trade amount
- `ui_config.json` — preset ladders and UI settings (editable from the settings modal)
- `.env` — RPC, keys, builder URLs (private repo only)

## API shape

JSON endpoints for balances, swap quote/execute, USDC/ETH sends, gas estimates, nonce status, stuck checks, cancel actions, plus WebSocket live logs. Full route list in the private `ARCHITECTURE.md`.

## Quick start

```bash
# private repo — configure .env and gas JSON first
python3 dnx_swap_webapp_optimized.py
```

See [REPOS.md](REPOS.md) for repository links.

---

**Made by [Logic Encoder](https://logicencoder.com)** · [GitHub](https://github.com/logicencoder) · [Contact](https://logicencoder.com/contact/)
