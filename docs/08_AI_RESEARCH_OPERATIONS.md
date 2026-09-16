# Destiny — AI Research Operations

> Status: Active operating policy
> Principle: AI proposes and investigates; people approve decisions and
> production use.

## 1. Purpose

This document assigns research and engineering work to AI tools by evidence
need, not by brand preference. It prevents a polished answer from becoming a
source of truth without a reproducible source, independent check, and a human
decision.

An AI output is working material. A cited primary source, a verified dataset,
or an approved internal decision record is the evidence that may enter
Destiny's production path.

## 2. Current candidate roster

| Candidate | Best initial role | Required control | Current disposition |
| --- | --- | --- | --- |
| Codex | Repository implementation, tests, packaging, and change review | Run tests/builds; inspect the actual diff; do not treat generated code as verified without execution. | Active engineering tool |
| ChatGPT Deep Research | Multi-source synthesis, source-plan review, and structured research reports | Restrict to appropriate sources where needed; verify citations before use. | Active research coordinator when available |
| Perplexity Research | Fast source discovery and market-research first pass | Check every key number at its original source; split large tasks because a long run previously stopped before completion. | Active discovery candidate |
| Claude | Independent code review, design critique, and adversarial review | Provide exact commit range; compare findings to the local diff and tests. | Active independent reviewer |
| Gemini Deep Research | Research plan and source-led report, especially when Google Search or user-approved Google sources are relevant | Review the proposed plan and citations; availability and limits depend on the account. | Candidate for the next cross-check |
| Grok | Alternative framing and current-discourse discovery | Treat web or social signals as leads, not evidence; independently verify material claims. | Discovery-only candidate |
| HyperCLOVA X / NAVER tools | Korean-language and Korea-context exploration | Confirm the exact product, source access, and commercial terms before production use. | Korean-market evaluation candidate |
| Meta models | Open-weight or research comparison where a specific accessible model is selected | Pin the model/version and retain the evaluation corpus. | Parked until a concrete use case exists |

The roster is not a purchase list and does not imply that every tool is enabled
for the account. A tool is activated only for a bounded task with a defined
expected output.

## 3. Task routing

| Task | Primary worker | Independent check | Acceptable output |
| --- | --- | --- | --- |
| Repository change | Codex | Claude or focused human review | Commit, diff, tests, build result |
| Calculation-rule source research | Deep Research or Perplexity | A second source plus rule-specific tests | Evidence ledger entry; no automatic promotion |
| Korean market demand | Perplexity or Gemini | Original platform/official statistics | Dated demand hypothesis and experiment proposal |
| Korean language or cultural phrasing | HyperCLOVA X candidate or another Korean-capable model | Human editorial review | Draft only, never an unsupported fact claim |
| Product decision | Human product owner | Relevant evidence record | Decision log entry |

## 4. Research report acceptance gate

Every report intended to influence product scope, rule data, or a spending
decision must contain:

1. A concrete question and research date.
2. A claim-to-source mapping with direct URLs or stable identifiers.
3. Source type, publication date, and any material limitation.
4. A separation between confirmed findings, hypotheses, and missing evidence.
5. A next action that can be accepted, rejected, or tested by a human.

Do not use an AI-generated summary, search-result snippet, blog ranking, or
another model's citation list as the final source for a production claim.

## 5. Operating cadence

- Use a short, bounded discovery task before invoking a long research run.
- Use one primary researcher and one independent verifier for consequential
  findings; do not ask several models the same broad question by default.
- Preserve the prompt, report, source list, model/product name, and date for
  any accepted research result.
- Record interrupted or incomplete runs as field evidence, not as failure
  hidden from later planning.
- Re-check tool availability, limits, pricing, and model behavior at the time
  of a purchase or workflow change; these are not stable project constants.

## 6. First evaluation backlog

1. Turn the prior Korea divination-market report into a claim/source table and
   recheck the few numbers that determine the MVP funnel.
2. Run a narrowly scoped Gemini cross-check of the highest-impact market
   claims, retaining its research plan and citations.
3. Create a Korean-language evaluation corpus for product microcopy and
   compare the eligible Korean-capable tools against human acceptance criteria.
4. Maintain the calculation-rule evidence ledger independently from market and
   language research; a good market result never promotes a Saju rule.

## 7. Vendor capability notes

- ChatGPT Deep Research can create a source-linked report from web, uploaded,
  and authorized connected sources; availability and limits vary by plan and
  workspace. [Official OpenAI documentation](https://help.openai.com/en/articles/10500283-research-faq)
- Gemini Deep Research can use Google Search by default and, when authorized,
  selected Google sources; it exposes a research-plan review step and has
  account-dependent limits. [Official Gemini documentation](https://support.google.com/gemini/answer/15719111?hl=en)
- Perplexity Research describes an iterative research workflow that performs
  many searches and returns a report. It remains a discovery tool until its
  cited sources are checked. [Perplexity help](https://www.perplexity.ai/help-center/en/articles/10738684-what-is-research-mode)
- IANA time and astronomical source research remain separate from model
  selection; AI tools may assist discovery but cannot replace their evidence
  gates.
