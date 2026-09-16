# Destiny — Korea MVP Input and Result UX

> Status: implementation-ready interaction specification; no client application
> exists in this repository yet.
> Depends on: `03_BIRTH_PROFILE_SPEC.md`, `04_SAJU_CALCULATION_SPEC.md`, and
> `11_KOREA_MVP_EXPERIMENT_SPEC.md`.

## 1. Product promise

The first experience is a short, calm path from recorded birth facts to a
reproducible Saju result. It should feel simple even when the calculation has
real limits.

The interface must never make the user decide a technical rule they do not
understand before seeing why it matters. It must also never silently invent a
missing birth time, place, lunar leap month, or time correction.

## 2. Screen map

```text
Welcome
  -> Birth date and calendar
  -> Birth time (known / unknown)
  -> Birth place (optional)
  -> Check facts
  -> Calculate
  -> Result
       -> calculation basis details
       -> alternative only when pillars differ
       -> start a new reading
```

Relationship/compatibility is not part of the original Korea MVP core scope.
If the entry experiment later enables it, it reuses this flow independently
for each voluntarily supplied profile and must not change the individual Saju
input contract.

## 3. Welcome

**Heading:** `내 사주 살펴보기`

**Body:** `알고 있는 출생 정보만 입력해 주세요. 모르는 정보는 비워 두어도 됩니다.`

**Primary action:** `시작하기`

**Supporting link:** `사주는 어떻게 계산하나요?`

The supporting explanation says only that birth date, time, and solar-term
boundaries affect the calculation; it does not expose advanced school terms.

## 4. Birth-date and calendar screen

Fields:

| Field | UI | Required | Behaviour |
| --- | --- | --- | --- |
| Display name | optional short text | no | Label results without requiring a real name. |
| Calendar | segmented choice: `양력` / `음력` | yes | No default that hides the choice. |
| Date | year, month, day picker | yes | Validate the date in the selected calendar. |
| Leap month | contextual choice | only if lunar date requires it | Hide for solar dates; offer `모름` when both lunar candidates are valid. |

**Inline error example:** `선택한 달력에서 존재하지 않는 날짜예요. 날짜를 다시 확인해 주세요.`

Do not ask for gender in the initial four-pillar flow. It is not needed for
the currently implemented core calculation. If a later approved rule requires
it (for example a Daewoon rule), ask then, explain why, and permit an unknown
value where the rule supports it.

## 5. Birth-time screen

**Question:** `태어난 시간을 알고 있나요?`

Choices:

- `알아요` → hour and minute input, with `분은 잘 몰라요` option.
- `몰라요` → continue with date-only calculation.

When unknown, show:

> 출생시간 없이도 연주·월주·일주는 계산할 수 있어요. 시주와 시주 기반 해석은 제외돼요.

When time is entered, validate the recorded local time only. Never prefill
midnight, noon, or the current time. The UI records the known precision
(`hour`, `minute`, or `unknown`) rather than pretending all times are equally
exact.

## 6. Birth-place screen

**Question:** `태어난 곳을 알려 주세요`  
**Support text:** `도시 정도면 충분해요. 잘 모르겠다면 건너뛸 수 있어요.`

Use place search with a visible selected city/country. Do not request an exact
address. Preserve the original typed place label alongside the normalised
place if one is resolved.

If location is missing, the basic legal-local-time calculation may continue
when the supported locale/timezone is otherwise known. Do not offer or apply
solar-time correction without a sufficiently resolved location and its
documented evidence gate.

## 7. Check-facts screen

Show a compact editable summary before calculation:

```text
1990년 5월 10일 · 양력
출생시간 23:35 · 분 단위 기록
출생지 서울, 대한민국
```

Under it, show the default in plain language:

> 기본 계산은 출생기록의 현지 시각과 절기 기준을 사용해요.

**Primary action:** `사주 계산하기`  
**Secondary action:** `수정하기`

No advanced-profile picker belongs on this screen. The user learns about an
alternative only after the system has established that it changes the
structured result.

## 8. Result screen

The result has three deliberately separated layers.

### 8.1 Calculated facts

Show four pillars (or three when time is unknown), calculation status, and
plain labels. A partial result must visibly say what is omitted.

```text
계산 결과
연주 · 월주 · 일주 · 시주

출생시간이 없어 시주는 포함하지 않았어요.
```

### 8.2 Interpretation

Show interpretation as tendencies and reflection prompts, never certainty.

Required footer:

> 이 결과는 자기 이해를 돕는 해석적 참고 자료예요. 건강·법률·투자·안전 관련 결정은 전문가와 상의해 주세요.

### 8.3 Calculation basis

A collapsed `계산 기준 보기` panel shows:

- selected profile label in plain Korean;
- calculation time basis;
- solar-term dataset/version;
- partial/ambiguous warnings;
- an easy path to edit the entered facts.

Technical identifiers can appear only as secondary detail for reproducibility.

## 9. Meaningful alternative choice

Only show this card when a supported alternative profile changes structured
pillars.

**Heading:** `날짜 기준에 따라 결과가 달라질 수 있어요`

**Body:**
`밤 11시 이후 출생 기록은 날짜를 바꾸는 기준에 따라 일주가 달라질 수 있어요. 두 기준을 비교해 보고 선택할 수 있어요.`

Actions:

- `기본 기준으로 보기`
- `기록된 날짜 기준과 비교하기`

The comparison view identifies *which* pillar changes and retains both profile
labels. It must not claim either choice is more correct for every tradition.

If the alternative does not change the pillars, no card, alert, or hidden
tracking event is shown.

## 10. Loading, errors, and recovery

| State | User-facing copy | Available action |
| --- | --- | --- |
| Calculating | `출생 정보를 바탕으로 계산하고 있어요.` | Wait; do not show a fabricated partial result. |
| Missing birth time | `출생시간 없이 계산할 수 있는 범위로 결과를 만들었어요.` | Edit time later. |
| Ambiguous lunar leap month | `평달과 윤달 중 어느 쪽인지 확인이 필요해요.` | Choose, or inspect clearly separated candidates if supported. |
| Unsupported/uncertain time data | `이 출생 정보에 적용할 수 있는 검증된 시간 기준이 아직 준비되지 않았어요.` | Edit facts; no guessed fallback. |
| Calculation data unavailable | `현재 이 날짜의 검증된 계산 데이터를 제공하지 못해요.` | Try another request later; preserve entered facts locally only if the user asks. |

Never phrase a data limitation as the user's mistake.

## 11. Accessibility and privacy acceptance checks

- Every choice is keyboard-operable and has an explicit text label.
- The result remains understandable without colour alone; pillars and warnings
  use text labels.
- Date/time format follows Korean conventions and works with screen readers.
- No birth data is sent to analytics as raw event properties.
- No result is saved, shared, or sent to an LLM without a separately disclosed
  implementation decision and the user's appropriate action.

## 12. Implementation boundary

This repository currently contains the calculation library and test fixtures,
not a web/mobile client, API, account system, calendar conversion service, or
interpretation service. Before UI code begins, the project needs a selected
client stack and a service contract that turns validated `RawBirthInput` into
the existing calculation engine's supported inputs without bypassing dataset
verification.
