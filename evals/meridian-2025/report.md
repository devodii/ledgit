# Eval report: meridian-2025

Generated 2026-11-11 20:37 UTC. Extraction and judging: `provider=claude_code model=claude-sonnet-5-5 prompt=v3`.

## Funnel

| Stage | Count |
| --- | ---: |
| Videos discovered | 61 |
| Transcripts fetched | 61 (0 manual, 61 auto) |
| Candidate claims extracted | 445 |
| Accepted by the judge | 160 |
| Kept after rank and trim | 120 |
| Public registry | 13 |
| Review queue | 107 |

## Quote integrity

Independent re-check of every public quote against the stored transcript: **13 of 13 verbatim**.

## Judge

Mean judge confidence on accepted claims: **0.655**.

| Confidence | Claims |
| --- | ---: |
| 0.2-0.4 | 4 |
| 0.4-0.6 | 48 |
| 0.6-0.8 | 63 |
| 0.8-1.0 | 45 |

Of candidates the extractor scored 0.8 or higher on both specificity and verifiability, the judge accepted **77%**.

## Drops by stage

| Stage | Reason | Count |
| --- | --- | ---: |
| resolve | no_relevant_evidence | 140 |
| write | low_confidence | 61 |
| write | nothing_checkable | 46 |
| judge | judge:not_checkable | 197 |
| judge | judge:org_incorrect | 10 |
| judge | judge:summary_not_faithful | 78 |
| rank | duplicate | 18 |
| rank | over_talk_cap | 14 |
| rank | over_target | 8 |
| extract | llm_output_unusable | 1 |
| extract | org_not_in_source | 42 |
| extract | quote_not_verbatim | 24 |

## Coverage of the public registry

| Measure | Value |
| --- | ---: |
| Speaker named | 100% |
| Domain resolved | 69% |
| Country known | 69% |
| SCF award found | 8% |
| At least one evidence item | 100% |

Claim types: partner_launch 5, protocol_feature 7, roadmap 1

Evidence kinds: asset_issuer 6, protocol_upgrade 7

Where facts came from (claims citing each source): horizon 1, lumenloop 9, stellar_expert 9, stellar_toml 9, stellarlight 18, talk 7

Caption source: auto 13

## Verification

Verdicts: live 13

Check outcomes: live 37

Verdict changes recorded: 14

## Human review

No labels yet. Fill `review-sample.yaml` and rerun to get a precision estimate.

## Yield per talk

| Talk | Candidates | Judge accepted | Public |
| --- | ---: | ---: | ---: |
| Supercharged Smart Contracts: Conflict-Free Parallelism & Protocol Cac | 15 | 11 | 5 |
| Lightning Talks Featuring Ondo Finance, Etherfuse, Kredete | Meridian  | 9 | 3 | 2 |
| Money on Their Terms: How MoneyGram is Bridging Finance & Crypto for F | 4 | 1 | 1 |
| PYUSD, PayFi, and the Future of Accessing Capital | Meridian 2025 | 11 | 3 | 1 |
| Reflector: From Concept to DAO Governed Oracle | Meridian 2025 | 23 | 10 | 1 |
| Talks w/ Kredete, 21x, Meru, Cheesecake Labs, Solv Finance, & The Wall | 15 | 5 | 1 |
| Building Your Data Stack: Stellar Open Source Tools Meet Goldsky Infra | 11 | 5 | 1 |
| Stellar Analytics on a Shoestring Budget | Meridian 2025 | 13 | 2 | 1 |
| We've Tokenized Everything: Now What?! | Meridian 2025 | 6 | 0 | 0 |
| The Future of Purposeful Technology | Meridian 2025 | 9 | 2 | 0 |
| Scalability not Scarcity: Ensuring Long-term Equitable Access to Block | 8 | 3 | 0 |
| Local Solutions, Global Impact: Building for Emerging Markets | Meridi | 8 | 0 | 0 |
| Eliminating Transaction Limits with zk | Meridian 2025 | 9 | 4 | 0 |
| Confidential Tokens on Stellar — A Smart-Contract Approach | Meridian  | 5 | 2 | 0 |
| Scaling the Rails: Enterprise-Grade Infrastructure on Stellar | Meridi | 4 | 1 | 0 |
| How Security Changes in the Age of Vibe Coding | Meridian 2025 | 7 | 2 | 0 |
| From Cards to Code: How Stablecoins Will Rewire Everyday Payments | Me | 0 | 0 | 0 |
| From Vision to Vindication: A Decade of Building the Future of Payment | 0 | 0 | 0 |
| First to the Future: How Pantera Pioneered Institutional Blockchain In | 2 | 0 | 0 |
| The Distribution Opportunity | Meridian 2025 | 2 | 0 | 0 |
| Designing for Trust: Rethinking UX in Web3 | Meridian 2025 | 12 | 6 | 0 |
| Inside Stellar: Features That Power Great Developer Tools | Meridian 2 | 18 | 5 | 0 |
| Transforming Imagination into Income: A Virtual Fireside Chat with Idr | 6 | 2 | 0 |
| Stablecoin Lending for a New Era of Global Finance | Meridian 2025 | 0 | 0 | 0 |
| Private Transactions for Stellar | Meridian 2025 | 5 | 1 | 0 |
| The Intent-Driven Future with NEAR Intents | Meridian 2025 | 6 | 5 | 0 |
| What We've Built and Where We're Headed: Scaling Stellar Core for the  | 9 | 3 | 0 |
| Optimizing High Speed Through Research | Meridian 2025 | 5 | 0 | 0 |
| Around the World: Hot Topics in Regional Crypto Regulation | Meridian  | 1 | 0 | 0 |
| Mapping the Stellar Network: A Live Look with Messari and Artemis | Me | 15 | 8 | 0 |
| The Security Mindset: Building Vulnerability-Free Soroban Smart Contra | 4 | 0 | 0 |
| The Convergence of Global Finance and Web3 | Meridian 2025 | 4 | 0 | 0 |
| Welcome to Meridian: A Blueprint for the Future of Finance | Meridian  | 11 | 3 | 0 |
| Restoring Dignity and Empowering Communities Through Digital Identity  | 3 | 0 | 0 |
| Brazil's Fintech Revolution: Going Global | Meridian 2025 | 0 | 0 | 0 |
| Colonizing Mars: The Journey of Building a Smart Wallet | Meridian 202 | 3 | 1 | 0 |
| It's Never Been Better to Build On Stellar | Meridian 2025 | 12 | 7 | 0 |
| Charting Course With Freighter | Meridian 2025 | 10 | 5 | 0 |
| Revenue vs. Roadmaps: What VCs Actually Fund | Meridian 2025 | 0 | 0 | 0 |
| Stellar Shark Tank | Meridian 2025 | 17 | 6 | 0 |
| Meridian Closing: The Blueprint Becomes Reality | Meridian 2025 | 10 | 1 | 0 |
| An Eye for the Future: Franklin Templeton's Bold Moves on Blockchain | | 11 | 4 | 0 |
| Engineering Stellar Smart Wallets for Real-World Activation | Meridian | 9 | 6 | 0 |
| The Machines Can Code and Stellar is Ready | Meridian 2025 | 2 | 0 | 0 |
| Open, Modular, Minimalist Infrastructure for Stellar and Beyond | Meri | 12 | 4 | 0 |
| Lightning Talks Featuring Arculus, PwC US, Alfred Pay and Mercado Bitc | 9 | 3 | 0 |
| The Roadmap for Privacy on Stellar | Meridian 2025 | 19 | 7 | 0 |
| Leveraging the Malicious Mindset | Meridian 2025 | 2 | 0 | 0 |
| Cracking the Code on Cross‑Chain Simplicity | Meridian 2025 | 3 | 1 | 0 |
| Meridian 2025 Recap | 0 | 0 | 0 |
| Bringing Innovation to Public Projects: Lessons Learned | Meridian 202 | 3 | 0 | 0 |
| Stellar Disbursement Platform: From a Payouts Tool to a One-Stop-Shop  | 4 | 4 | 0 |
| How Beans Delivers Optimized Yield Using Defindex and Blend | Meridian | 17 | 6 | 0 |
| Welcome to Ipanema: Meridian's Innovation Stage | Meridian 2025 | 6 | 1 | 0 |
| Crypto Doesn't Have to Be Hard | Meridian 2025 | 0 | 0 | 0 |
| Rapid Application Development with Scaffold Stellar | Meridian 2025 | 10 | 6 | 0 |
| Innovation AMA | Meridian 2025 | 4 | 1 | 0 |
| The Innovation Imperative: Building Cities That Shape Tomorrow | Merid | 3 | 1 | 0 |
| A Vision for Universal Interoperability | Meridian 2025 | 7 | 4 | 0 |
| Operationalizing Blockchain in Banking: How Institutions are Making it | 5 | 2 | 0 |
| The RWA Revolution: How Traditional Assets Are Finding Their Way Oncha | 7 | 3 | 0 |
