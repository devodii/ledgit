# Eval report: meridian-2025

Generated 2026-11-11 19:39 UTC. Extraction and judging: `provider=claude_code model=claude-sonnet-5-5 prompt=v1`.

## Funnel

| Stage | Count |
| --- | ---: |
| Videos discovered | 61 |
| Transcripts fetched | 61 (0 manual, 61 auto) |
| Candidate claims extracted | 231 |
| Accepted by the judge | 80 |
| Kept after rank and trim | 40 |
| Public registry | 40 |
| Review queue | 0 |

## Quote integrity

Independent re-check of every public quote against the stored transcript: **40 of 40 verbatim**.

## Judge

Mean judge confidence on accepted claims: **0.734**.

| Confidence | Claims |
| --- | ---: |
| 0.2-0.4 | 1 |
| 0.4-0.6 | 7 |
| 0.6-0.8 | 37 |
| 0.8-1.0 | 35 |

Of candidates the extractor scored 0.8 or higher on both specificity and verifiability, the judge accepted **55%**.

## Drops by stage

| Stage | Reason | Count |
| --- | --- | ---: |
| judge | judge:not_checkable | 103 |
| judge | judge:org_incorrect | 2 |
| judge | judge:summary_not_faithful | 46 |
| rank | over_target | 40 |
| extract | llm_output_unusable | 1 |
| extract | org_not_in_source | 46 |
| extract | quote_not_verbatim | 23 |

## Coverage of the public registry

| Measure | Value |
| --- | ---: |
| Speaker named | 90% |
| Domain resolved | 52% |
| Country known | 45% |
| SCF award found | 15% |
| At least one evidence item | 20% |

Claim types: partner_launch 21, protocol_feature 10, roadmap 9

Evidence kinds: asset_issuer 3, protocol_upgrade 5

Where facts came from (claims citing each source): homepage 2, lumenloop 18, stellar_expert 12, stellar_toml 11, stellarlight 30

Caption source: auto 40

## Verification

Verdicts: live 8, no_trace_found 32

Check outcomes: live 45

Verdict changes recorded: 55

## Human review

No labels yet. Fill `review-sample.yaml` and rerun to get a precision estimate.

## Yield per talk

| Talk | Candidates | Judge accepted | Public |
| --- | ---: | ---: | ---: |
| What We've Built and Where We're Headed: Scaling Stellar Core for the  | 8 | 5 | 4 |
| Stellar Disbursement Platform: From a Payouts Tool to a One-Stop-Shop  | 6 | 5 | 4 |
| Reflector: From Concept to DAO Governed Oracle | Meridian 2025 | 8 | 5 | 3 |
| The Roadmap for Privacy on Stellar | Meridian 2025 | 5 | 4 | 3 |
| Supercharged Smart Contracts: Conflict-Free Parallelism & Protocol Cac | 8 | 4 | 3 |
| Charting Course With Freighter | Meridian 2025 | 8 | 2 | 2 |
| Building Your Data Stack: Stellar Open Source Tools Meet Goldsky Infra | 6 | 4 | 2 |
| We've Tokenized Everything: Now What?! | Meridian 2025 | 2 | 1 | 1 |
| Scalability not Scarcity: Ensuring Long-term Equitable Access to Block | 6 | 4 | 1 |
| Local Solutions, Global Impact: Building for Emerging Markets | Meridi | 6 | 1 | 1 |
| Lightning Talks Featuring Ondo Finance, Etherfuse, Kredete | Meridian  | 8 | 2 | 1 |
| Scaling the Rails: Enterprise-Grade Infrastructure on Stellar | Meridi | 2 | 1 | 1 |
| How Security Changes in the Age of Vibe Coding | Meridian 2025 | 5 | 2 | 1 |
| PYUSD, PayFi, and the Future of Accessing Capital | Meridian 2025 | 8 | 1 | 1 |
| The Intent-Driven Future with NEAR Intents | Meridian 2025 | 5 | 2 | 1 |
| Welcome to Meridian: A Blueprint for the Future of Finance | Meridian  | 8 | 2 | 1 |
| Talks w/ Kredete, 21x, Meru, Cheesecake Labs, Solv Finance, & The Wall | 7 | 3 | 1 |
| Meridian Closing: The Blueprint Becomes Reality | Meridian 2025 | 4 | 2 | 1 |
| An Eye for the Future: Franklin Templeton's Bold Moves on Blockchain | | 7 | 3 | 1 |
| Open, Modular, Minimalist Infrastructure for Stellar and Beyond | Meri | 5 | 1 | 1 |
| Lightning Talks Featuring Arculus, PwC US, Alfred Pay and Mercado Bitc | 5 | 2 | 1 |
| Cracking the Code on Cross‑Chain Simplicity | Meridian 2025 | 2 | 1 | 1 |
| Welcome to Ipanema: Meridian's Innovation Stage | Meridian 2025 | 5 | 2 | 1 |
| Rapid Application Development with Scaffold Stellar | Meridian 2025 | 6 | 3 | 1 |
| Stellar Analytics on a Shoestring Budget | Meridian 2025 | 6 | 2 | 1 |
| The RWA Revolution: How Traditional Assets Are Finding Their Way Oncha | 5 | 1 | 1 |
| The Future of Purposeful Technology | Meridian 2025 | 4 | 0 | 0 |
| Eliminating Transaction Limits with zk | Meridian 2025 | 4 | 2 | 0 |
| Confidential Tokens on Stellar — A Smart-Contract Approach | Meridian  | 6 | 2 | 0 |
| From Cards to Code: How Stablecoins Will Rewire Everyday Payments | Me | 0 | 0 | 0 |
| From Vision to Vindication: A Decade of Building the Future of Payment | 0 | 0 | 0 |
| Money on Their Terms: How MoneyGram is Bridging Finance & Crypto for F | 0 | 0 | 0 |
| First to the Future: How Pantera Pioneered Institutional Blockchain In | 2 | 0 | 0 |
| The Distribution Opportunity | Meridian 2025 | 2 | 0 | 0 |
| Designing for Trust: Rethinking UX in Web3 | Meridian 2025 | 0 | 0 | 0 |
| Inside Stellar: Features That Power Great Developer Tools | Meridian 2 | 3 | 1 | 0 |
| Transforming Imagination into Income: A Virtual Fireside Chat with Idr | 7 | 1 | 0 |
| Stablecoin Lending for a New Era of Global Finance | Meridian 2025 | 0 | 0 | 0 |
| Private Transactions for Stellar | Meridian 2025 | 0 | 0 | 0 |
| Optimizing High Speed Through Research | Meridian 2025 | 0 | 0 | 0 |
| Around the World: Hot Topics in Regional Crypto Regulation | Meridian  | 0 | 0 | 0 |
| Mapping the Stellar Network: A Live Look with Messari and Artemis | Me | 6 | 0 | 0 |
| The Security Mindset: Building Vulnerability-Free Soroban Smart Contra | 0 | 0 | 0 |
| The Convergence of Global Finance and Web3 | Meridian 2025 | 0 | 0 | 0 |
| Restoring Dignity and Empowering Communities Through Digital Identity  | 2 | 0 | 0 |
| Brazil's Fintech Revolution: Going Global | Meridian 2025 | 0 | 0 | 0 |
| Colonizing Mars: The Journey of Building a Smart Wallet | Meridian 202 | 0 | 0 | 0 |
| It's Never Been Better to Build On Stellar | Meridian 2025 | 7 | 1 | 0 |
| Revenue vs. Roadmaps: What VCs Actually Fund | Meridian 2025 | 0 | 0 | 0 |
| Stellar Shark Tank | Meridian 2025 | 7 | 2 | 0 |
| Engineering Stellar Smart Wallets for Real-World Activation | Meridian | 6 | 2 | 0 |
| The Machines Can Code and Stellar is Ready | Meridian 2025 | 4 | 1 | 0 |
| Leveraging the Malicious Mindset | Meridian 2025 | 3 | 0 | 0 |
| Meridian 2025 Recap | 0 | 0 | 0 |
| Bringing Innovation to Public Projects: Lessons Learned | Meridian 202 | 0 | 0 | 0 |
| How Beans Delivers Optimized Yield Using Defindex and Blend | Meridian | 7 | 2 | 0 |
| Crypto Doesn't Have to Be Hard | Meridian 2025 | 2 | 0 | 0 |
| Innovation AMA | Meridian 2025 | 1 | 1 | 0 |
| The Innovation Imperative: Building Cities That Shape Tomorrow | Merid | 0 | 0 | 0 |
| A Vision for Universal Interoperability | Meridian 2025 | 4 | 0 | 0 |
| Operationalizing Blockchain in Banking: How Institutions are Making it | 3 | 0 | 0 |
