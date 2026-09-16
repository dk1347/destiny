# Saju calculation core

`destiny-saju` provides deterministic pillar primitives. It does not infer
calendar boundaries from an LLM.

## Verified scope

The bundled solar-term table is verified only for Asia/Seoul local instants
from **2026-01-01 00:00 +09:00** through **2026-12-31 23:59 +09:00**. A
lookup outside that interval fails closed with `SOLAR_TERM_DATA_UNAVAILABLE`.

The checked-in core rule table is intentionally `pending_verification`.
Production callers must provide a production-verified rule directory. The
`allow_unverified=True` option is for tests and controlled validation work,
not a production bypass.

## Four pillars

`four_pillars_for_datetime()` accepts an already-resolved, timezone-aware
Korea Standard Time (`+09:00`) `datetime`. The implementation applies these
boundaries consistently:

- Year pillar changes at the verified Ipchun instant.
- Month pillar uses the latest verified major solar term.
- Day pillar uses a verified sexagenary-day anchor.
- At Ja hour (23:00–23:59), the day and hour stem use the following civil
  date; year and month still use the original instant.

```python
from datetime import datetime, timedelta, timezone

from destiny_saju import RuleRegistry, four_pillars_for_datetime

KST = timezone(timedelta(hours=9))
registry = RuleRegistry(data_dir=production_verified_rule_directory)
pillars = four_pillars_for_datetime(datetime(2026, 2, 4, 5, 2, tzinfo=KST), registry)
```

Do not silently convert another timezone before calling this API: resolve the
birth instant to Korea Standard Time first, then pass the resolved local
datetime.
