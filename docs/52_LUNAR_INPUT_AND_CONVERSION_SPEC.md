# Lunar Input and Conversion Specification

> Status: design approved for implementation planning; no lunar conversion data
> or runtime dependency has been added yet.

## Decision

Destiny will accept lunar dates only as an explicitly selected input calendar.
The user must select `평달` or `윤달`; the application never guesses this from
the month number. Before Four Pillars calculation, the selected lunar date is
converted to and displayed as a Gregorian date.

## Official reference and supported range

The primary reference is KASI's [Lunar/Solar Calendar Conversion]
(https://astro.kasi.re.kr/life/pageView/8). The service documents lunar-to-
solar conversion, exposes separate ordinary-month and leap-month choices, and
publishes an input range of 59 BCE through 2050 CE.

This establishes the intended product behaviour, but does not by itself grant
permission to copy or redistribute its underlying data. Before implementation,
record the reuse/licence decision for the chosen source or dataset. Until
then, do not scrape KASI at runtime and do not ship an unreviewed conversion
table.

## API request contract

Replace the ambiguous date-only shape with one calendar-specific object:

```json
{
  "birth_calendar": "solar",
  "birth_date": "2026-09-18"
}
```

```json
{
  "birth_calendar": "lunar",
  "birth_lunar_date": {"year": 2026, "month": 8, "day": 8, "is_leap_month": false}
}
```

- `birth_calendar` is required and is either `solar` or `lunar`.
- A solar request has exactly one Gregorian ISO date.
- A lunar request has positive year, month `1..12`, day `1..30`, and a required
  Boolean `is_leap_month`.
- A time, when supplied, stays a separately labelled Korean civil local time.
- Reject mixed solar/lunar fields and omitted leap-month choice with a stable
  422 error; do not choose a default.

## Response contract

For lunar input, return the original input and verified conversion separately:

```json
{
  "input_calendar": "lunar",
  "input_lunar_date": {"year": 2026, "month": 8, "day": 8, "is_leap_month": false},
  "resolved_solar_date": "2026-09-18",
  "conversion_dataset_id": "<versioned-source-id>"
}
```

The UI states `음력 YYYY년 M월 D일 (평달/윤달) → 양력 YYYY-MM-DD` before
presenting pillars. This prevents users from mistaking the converted date for
their original birth-calendar entry.

## Error contract

| Situation | Code | User message direction |
| --- | --- | --- |
| Missing ordinary/leap selection | `LUNAR_LEAP_MONTH_REQUIRED` | Ask the user to select 평달 or 윤달. |
| Invalid lunar day/month combination | `INVALID_LUNAR_DATE` | Say that the lunar date does not exist. |
| Outside verified conversion range | `LUNAR_CALENDAR_DATA_UNAVAILABLE` | State the requested year is not yet supported. |
| Lunar date converts correctly but its solar-term data is unavailable | `SOLAR_TERM_DATA_UNAVAILABLE` | Keep the existing year-specific solar-term message. |

## Required test fixtures

1. One ordinary lunar month date converts to a known Gregorian date.
2. A real leap-month date converts differently from the same ordinary-month
   date.
3. Omitting `is_leap_month` fails; `false` is not silently assumed.
4. Invalid day 30 in a 29-day lunar month fails.
5. The first and final supported conversion dates behave correctly.
6. A converted date at a solar-term boundary still follows the ordinary
   solar-term coverage and boundary rules.
7. Existing solar-only requests remain backward compatible during migration,
   or receive a versioned API migration path before removal.

## Explicit exclusions

- No live KASI request while a user waits for a result.
- No lunar conversion beyond the verified conversion dataset range.
- No true-solar-time adjustment in this feature.
- No RAG access or changes.
