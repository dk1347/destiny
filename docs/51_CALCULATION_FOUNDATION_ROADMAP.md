# Calculation Foundation Roadmap

> Status: planning only. No item in this roadmap changes the current
> production calculation profile unless its acceptance criteria are met.

## Product principle

Destiny must show which calendar and time basis produced a result. It must not
silently convert an input, guess a leap month, or apply true-solar-time
correction without the user's informed choice.

## Delivery order

| Phase | Scope | User-facing rule | Release gate |
| --- | --- | --- | --- |
| 1 | Solar (Gregorian) input hardening | The current default remains a Korean local Gregorian birth date/time. | Existing date, time, timezone, and out-of-coverage tests remain green. |
| 2 | Lunar-calendar conversion | Lunar date input is explicitly labelled and converted to a recorded Gregorian date before Four Pillars calculation. | Verified conversion source, ordinary-date tests, and conversion-result display. |
| 3 | Leap-month support | A leap-month toggle appears only for lunar input and is never inferred from a duplicated month number. | Verified leap-month fixtures and clear converted-date disclosure. |
| 4 | Historical Korean civil time | The selected civil-time policy covers historical standard-time and DST transitions in the supported date range. | Versioned timezone evidence and transition-boundary tests. |
| 5 | Verified solar-term coverage | Expand only reviewed KST annual ranges; unavailable years remain unavailable. | `docs/16_SOLAR_TERM_DATA_RELEASE_GATE.md` and `docs/50_SOLAR_TERM_SOURCE_ACQUISITION_LEDGER.md` completed per year. |
| 6 | True solar time (optional) | It is an opt-in comparison mode, never an invisible replacement for standard calculation. | Location requirement, published correction method, and before/after boundary tests. |

## Input and result contract

### Calendar selection

- Default: `양력`.
- `음력` requires year, month, day, and an explicit `윤달 여부` selection.
- The calculation request stores both the original input and the converted
  Gregorian result; the result screen shows both.
- If a conversion cannot be verified for the requested date, return a clear
  unavailable result. Do not choose a plausible Gregorian date.

### Time basis

- Default profile: Korean civil local time, as currently documented.
- Historical offset/DST policy is versioned data, not an ad-hoc rule in the UI.
- True solar time requires a usable birth location (at minimum a selected city
  with an audited longitude); a free-text place name alone is insufficient.
- A true-solar-time result states the selected place, longitude source,
  correction amount, and whether any pillar changed.

## What must stay separate

1. Lunar conversion determines the civil Gregorian instant used as input.
2. Solar-term data determines year/month-pillar boundaries for that instant.
3. Historical civil-time policy determines what the recorded local clock time
   meant on that date.
4. True solar time is an optional further transformation, not a substitute for
   lunar conversion or solar-term data.

Keeping these layers separate makes a disagreement traceable and prevents a
fix in one layer from changing another invisibly.

## Immediate next action

Before implementation, write the lunar-conversion source and data-license
decision. It must identify the official Korean source or licensed dataset,
supported year range, leap-month representation, timezone, and reuse terms.
Only then should the UI or API accept lunar input.

## Explicit non-goals for the first release

- No automatic birthplace geocoding.
- No claim that true solar time is universally more correct.
- No historical date support beyond the verified solar-term and calendar-data
  ranges.
- No modifications to the legacy RAG database.
