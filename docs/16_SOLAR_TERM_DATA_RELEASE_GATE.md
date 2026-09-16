# Destiny — Solar-term Data Release Gate

> Status: implementation gate; this document does not approve a public birth-year
> range by itself.

## 1. Purpose

The Four Pillars engine must not infer solar-term instants at runtime from a
third-party Manse Ryeok site. It ships a versioned dataset instead. This gate
defines how an expanded dataset may become eligible for a Korea MVP release.

The currently bundled `solar_term_instants_v1` covers only the 2026 boundary
set. It is suitable for deterministic development fixtures, not evidence that
all user birth years are supported.

## 2. Source hierarchy

1. **Primary:** Korea Astronomy and Space Science Institute (KASI) monthly
   calendar/almanac material. KASI describes the material as the basis for
   lunar-date and 24-term calendar production.
2. **Independent comparison:** National Astronomical Observatory of Japan
   (NAOJ) Calendar and Ephemeris Computation page, using KST (UTC+9) output.
3. **Definition/reference only:** the documented solar-longitude model and
   generator selected by Destiny. A library, commercial Manse Ryeok site, or
   search-result snippet cannot be the sole production source.

Every imported row records the source URL or publication identifier, retrieval
date, declared timezone, source precision, and dataset-generator version.
Copyright and reuse terms must be checked before storing or redistributing
source-derived values; public availability is not by itself a reuse licence.

## 3. Range decision rule

Do not publish a vague claim such as “all dates supported.” Before release,
product and engineering select an explicit inclusive Gregorian birth-year
range. The range is allowed only when every year in it has a complete 24-term
boundary set plus the immediately preceding boundary needed at the start of
the range.

Until that decision is approved, the engine must expose a structured
out-of-coverage result rather than silently using a nearby year or a web
lookup.

## 4. Dataset promotion checklist

`production_verified` requires all of the following.

1. Complete, ordered 24-term entries for every approved year and required
   start boundary.
2. KST offset and minute precision recorded for every entry.
3. Primary-source capture and independent NAOJ comparison for every boundary.
4. A documented discrepancy policy. A difference of even one minute is
   investigated and recorded; it is not rounded away because a user may be
   born at that boundary.
5. Provenance, generation procedure, and licence/reuse assessment stored with
   the dataset version.
6. Regression fixtures at the instant before, exactly at, and immediately
   after each month-changing boundary; include Ipchun separately because it
   changes the year pillar.
7. A clean installed-wheel test that loads the dataset without a repository
   checkout or network connection.

## 5. Initial release recommendation

Choose the first public range for evidence coverage, not marketing breadth.
Build a small contiguous pilot range only after source access and comparison
are validated end-to-end, then expand in reviewed batches. There is no basis
yet to select the pilot years or advertise broad historical coverage.

## 6. References

- KASI monthly calendar data: https://astro.kasi.re.kr/kor/life/post/calendarData
- KASI astronomical almanac publications: https://www.kasi.re.kr/kor/publication/post/publication?clsf_cd=pub07
- NAOJ 24 solar terms calculator: https://eco.mtk.nao.ac.jp/cgi-bin/koyomi/cande/phenomena_sy_en.cgi
- Existing Destiny data-source policy: `docs/05_CALCULATION_DATA_SOURCES.md`
