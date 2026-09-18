# True Solar Time — Optional Comparison Specification

> Status: design only. This feature must not alter the default calculation
> profile or existing results.

## Product decision

True solar time is an **opt-in comparison**. The default Destiny result uses
the recorded Korean civil time. A user may request a second result that shows
whether a declared true-solar-time method changes a pillar at a boundary.

The product must never describe the option as universally more correct. It is
a different convention requiring a birthplace, a longitude source, and an
explicit calculation method.

## Scientific references

- KASI's [2024 Korean Astronomical Almanac](https://astro.kasi.re.kr/file/astro_almanac_pdf/20231023135218580.pdf)
  defines the equation of time as `apparent solar time − mean solar time` and
  publishes values at KST noon.
- NOAA's [General Solar Position Calculations](https://gml.noaa.gov/grad/solcalc/solareqns.PDF)
  documents a time-offset calculation using equation of time, longitude, and
  UTC offset.
- NIST's [solar-time reference](https://www.nist.gov/pml/time-and-frequency-division/popular-links/time-frequency-z/time-and-frequency-z-s-so)
  explains that apparent and mean solar time differ by the equation of time.

These references support a transparent, reproducible method. They are not a
claim that a particular traditional interpretation convention is mandatory.

## Required inputs

| Field | Requirement |
| --- | --- |
| Birth civil date/time | Already required by the ordinary time-known flow. |
| Birthplace | User selects a supported Korean city; no ambiguous free-text geocoding. |
| Longitude | Comes from a versioned city dataset with source and precision. |
| Civil-time policy | Resolved first under `docs/53_KOREAN_HISTORICAL_CIVIL_TIME_POLICY.md`. |
| Solar-time method id | Versioned and returned with the result. |

## Calculation sequence

1. Resolve the recorded Korean civil time using the historical civil-time
   policy, including any historical DST rule.
2. Convert it to the corresponding standard-time basis before applying a
   longitude correction.
3. Apply the selected method's equation-of-time value and longitude correction
   relative to the Korean standard meridian (135°E for UTC+09:00).
4. Produce a second local datetime with a signed correction in minutes and
   seconds; retain the original civil datetime unchanged.
5. Run the normal Four Pillars engine for both profiles only if both required
   solar-term records are verified.

The initial documented formula is:

```text
true_solar_correction_minutes
  = equation_of_time_minutes + 4 × (birth_longitude_degrees − 135)
```

Its sign convention, precision, astronomical ephemeris, and leap-year handling
must be locked by `solar_time_method_id`; a developer must not substitute a
web calculator during a user request.

## Result contract

Show a comparison card only after explicit opt-in:

```text
기본 기준: 한국 표준시 12:30
출생지: 부산광역시 (129.0756°E)
진태양시 보정: −23분 18초
비교 시각: 12:06:42
기둥 변경: 없음 / 시주 변경
```

The actual response also records `city_dataset_id`, `solar_time_method_id`,
`equation_of_time_source`, correction precision, and both calculation-profile
ids.

## Safety and tests

1. Default calculation output is byte-for-byte unchanged when the option is
   not selected.
2. Every supported city has an audited longitude and attribution.
3. Tests cover an east/west longitude correction, leap-year date, a change
   across a two-hour branch boundary, and a result with no pillar change.
4. Historical DST tests first resolve civil time and then apply the solar-time
   method; no double one-hour correction is allowed.
5. Missing birthplace or unsupported city returns an unavailable result rather
   than using Seoul as an unannounced substitute.

## Explicit exclusions

- No automatic use for all users.
- No foreign birthplace support in the Korean MVP.
- No online geocoder or solar calculator in the production request path.
- No claim that solar-time precision exceeds the input-time precision.
