# Destiny — Korea MVP Experiment Specification

> Status: product experiment specification; no tracking implementation yet.
> Decision basis: `09_KOREA_MVP_DEMAND_HYPOTHESES.md` and
> `10_KOREA_MVP_DEMAND_CLAIM_AUDIT.md`.

## 1. Objective

Choose the most useful free first experience without claiming that an external
market report has already selected a winner.

The experiment compares two user-visible entry paths:

- **A — Daily reading:** a short reading for the selected date.
- **B — Compatibility / relationship reading:** a short reading for a person
  or relationship context the user voluntarily supplies.

Both paths use the same verified calculation core and must disclose the
calculation profile that produced the result.

## 2. Eligible participants and assignment

- A participant must reach a completed, valid free result.
- Assignment is random and persistent for that anonymous session or account.
- Do not reassign a participant merely because they return later.
- Exclude internal testing, malformed requests, and users who declined the
  required data notice.
- Do not use age, gender, inferred relationship status, or financial data to
  choose a variant.

## 3. Minimum experience flow

```text
start
  -> choose A or B entry path
  -> enter only data needed for that path
  -> show calculation settings in plain language
  -> display free result and interpretation disclaimer
  -> offer one optional relevant follow-up
  -> record voluntary completion and later return
```

The result screen must say that it is an interpretive reading for reflection
and entertainment, not a fact, diagnosis, legal/financial instruction, or
guarantee about another person.

## 4. Calculation-setting behaviour

Default behaviour is automatic and plain-language first:

- Use the documented default calculation profile.
- If an alternative profile would change the structured pillars, reveal a
  concise choice with an explanation of the difference; do not force the user
  to learn terms such as “Ja hour” or “true solar time.”
- Persist the selected/default profile with the result so the result is
  reproducible.
- If timezone, place, or data precision is insufficient for an optional
  correction, do not silently apply it.

This preserves the rule in `04_SAJU_CALCULATION_SPEC.md`: user choice exists
when it materially affects the outcome, while the common path stays simple.

## 5. Metrics and decision thresholds

| Metric | Definition | Why it matters | Guardrail |
| --- | --- | --- | --- |
| Start rate | assigned entry path opened / eligible landing views | Initial relevance | Never treat it as purchase intent. |
| Completion rate | free result displayed / started path | Flow clarity and calculation reliability | Split failures caused by data validation from voluntary exits. |
| Seven-day return | participant returns voluntarily within seven days / completed result | Repeat relevance | Do not use notifications solely to inflate this value. |
| Follow-up opt-in | voluntary follow-up opened / completed result | Relevance of the next question | Keep wording and prominence equivalent between variants. |
| Paid conversion | completed approved purchase / completed result | Value proposition, only in a separately approved paid test | Keep price, refund policy, and disclosure identical across variants. |
| Support or refund signal | relevant support/refund contacts / completed result | User harm and comprehension | Stop or revise a flow if this signal rises materially. |

Do not declare a winner from a small, seasonal, or unequally exposed sample.
Before launch, the product owner must define the minimum sample, observation
window, and decision rule. Until then the result is descriptive only.

## 6. Event data minimisation

Record only the minimum operational events needed to calculate the metrics:

- anonymous assignment identifier;
- variant (`daily` or `compatibility`);
- timestamp and flow state;
- calculation-profile identifier and whether an alternative changed pillars;
- validation/error category without raw birth data;
- result displayed, optional follow-up opened, voluntary return, and approved
  payment outcome where applicable.

Do not place raw birth date/time, birthplace, names, relationship narrative,
full reading text, payment details, or sensitive inferred traits in generic
analytics events. Retention, deletion, consent, access controls, and any
account linkage require a separate privacy and implementation decision.

## 7. Interpretation and stop conditions

Interpretation order:

1. Verify that calculation and validation errors are not driving the result.
2. Compare completion and return before considering a paid follow-up.
3. Review support/refund signals and user feedback before expanding exposure.
4. Document the product-owner decision, including why the evidence is enough
   or insufficient.

Pause the experiment if a result presentation encourages harmful certainty,
causes a material rise in confusion/support contacts, or exposes a calculation
or privacy defect.

## 8. Out of scope

This specification does not implement analytics, payment, notifications,
accounts, recommendation logic, true-solar-time correction, or any claim that
one fortune topic has superior market demand. Those need independent technical,
privacy, and product decisions.
