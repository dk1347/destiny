# Destiny — Versioned Rule Data Specification

> Version: 0.1
> Phase: Core Calculation Engine — Data Layer
> Status: Draft for Architecture Review
> Depends on: `03_BIRTH_PROFILE_SPEC.md`, `04_SAJU_CALCULATION_SPEC.md`, `05_CALCULATION_DATA_SOURCES.md`, `06_ENGINE_CONTRACTS_AND_CORE_RULES.md`

---

## 1. Purpose and Scope

`06_ENGINE_CONTRACTS_AND_CORE_RULES.md`는 월간(오호둔), 시간(오서둔), 십신, 지장간, 합·충·형·파·해의 계산 규칙을 고정했다. 이 문서는 그 규칙들을 **버전 관리되는 JSON 데이터셋**으로 옮기기 위한 공통 schema와, 데이터셋별 구조·검증 규칙을 정의한다.

이 문서는 다음을 다루지 않는다.

- 계산 규칙 자체의 재정의 (`06_ENGINE_CONTRACTS_AND_CORE_RULES.md`의 규칙을 그대로 데이터로 옮긴다)
- 길흉·강약·해석 문장 (Interpretation Rule Layer의 책임)
- 절입시각·일주 anchor·대운 규칙의 실제 확정값 (§8 참조 — 별도 보류 데이터셋으로만 언급)

이 문서의 대상은 한국 MVP의 결정론적 사주 원국 계산 엔진(`kr_standard_v1`)이 사용하는 규칙 데이터에 한정한다.

---

## 2. Common Dataset Envelope

모든 계산 데이터셋 JSON 파일은 최상위에 다음 공통 필드(envelope)를 포함해야 한다.

```json
{
  "schema_version": "1.0",
  "dataset_id": "month_stem_rules_v1",
  "dataset_version": "1.0.0",
  "status": "draft",
  "source": {
    "type": "classical_rule",
    "description": "오호둔(五虎遁) 년간-월간 대응표, 명리학 표준 규칙",
    "reference": "04_SAJU_CALCULATION_SPEC.md §7.3, 06_ENGINE_CONTRACTS_AND_CORE_RULES.md §3.1"
  },
  "license": "internal-derived-no-third-party-copy",
  "generated_at": "2026-09-14T00:00:00Z",
  "generated_by": "manual",
  "data": { }
}
```

### 2.1 필드 정의

| 필드 | 필수 | 설명 |
|---|---|---|
| `schema_version` | 예 | 이 envelope 자체의 스키마 버전. envelope 구조(필드 이름·형식)가 바뀔 때만 올린다. |
| `dataset_id` | 예 | 데이터셋 논리 이름. `{concept}_v{n}` 형식을 쓰며 `n`은 breaking change 시 증가한다 (예: `month_stem_rules_v1`, `month_stem_rules_v2`). |
| `dataset_version` | 예 | 이 `dataset_id` 안에서의 semver. §9 버전 정책을 따른다. |
| `status` | 예 | §3의 4개 값 중 하나. |
| `source` | 예 | 데이터의 근거. `type`(예: `classical_rule`, `astronomical_dataset`, `independent_reference`), `description`, 필요하면 `reference`(문헌·URL·내부 문서 경로)를 포함하는 객체. 여러 출처가 있으면 배열로 확장 가능. |
| `license` | 예 | 재사용 조건. 제3자 데이터를 그대로 포함했다면 그 라이선스를 명시하고, 자체 정리한 고전 규칙이면 `internal-derived-no-third-party-copy`처럼 명확히 구분되는 값을 쓴다. `05_CALCULATION_DATA_SOURCES.md`가 참조 전용으로 지정한 자료(`rath/orrery` 등)는 이 필드에 출처로 등장할 수 없다. |
| `generated_at` | 예 | ISO-8601 UTC. 데이터 파일이 마지막으로 생성/수정된 시각(사람이 손으로 정리했어도 기록). |
| `generated_by` | 아니오 | `manual` \| `script:<name>@<version>` 등. 생성 스크립트가 있으면 재현을 위해 기록을 권장한다. |
| `data` | 예 | 데이터셋별 본문. §5, §8에서 구조를 정의한다. |

### 2.2 파일 위치 규약

- Production 후보 데이터: `data/saju/<dataset_id>.json`
- 아직 검증되지 않았거나 후보만 있는 데이터: `data/saju/<dataset_id>_candidates.json` 또는 §7의 fixture 규약을 따른다.
- 하나의 `dataset_id`에 대해 동시에 존재하는 production 파일은 하나뿐이어야 한다. 이전 버전은 git 이력으로 추적하며 파일명에 과거 버전을 남기지 않는다.

---

## 3. Status Enum and Production Load Rules

```text
draft                 초안. 값이 아직 검토되지 않았을 수 있다.
pending_verification  값은 정리됐으나 독립 검증/승인이 끝나지 않았다.
production_verified   검증 게이트를 통과했고 production 계산 경로에서 사용할 수 있다.
deprecated            더 이상 production에서 사용하지 않는다. 과거 결과 재현을 위해 보관한다.
```

### 3.1 로드 규칙

1. **Production 계산 경로**는 `status == "production_verified"`인 데이터셋만 로드한다. 그 외 상태의 데이터셋을 요청하면 엔진은 조용히 대체값을 쓰지 않고 `DATASET_NOT_PRODUCTION_VERIFIED`를 반환하며 해당 계산을 `blocked` 처리한다 (`06_ENGINE_CONTRACTS_AND_CORE_RULES.md` §7, §6.3).
2. **개발·테스트 경로**(단위 테스트, fixture 회귀 테스트, 로컬 개발)는 `draft`와 `pending_verification` 데이터셋을 명시적으로 지정해 로드할 수 있다. 이 경로는 반드시 별도 설정/플래그로 켜야 하며 기본값이어서는 안 된다.
3. **`deprecated`**는 어느 경로에서도 새로 로드하지 않는다. 과거에 `deprecated` 데이터셋으로 생성된 결과의 `provenance`를 재현·검증할 때만 참조용으로 읽는다.
4. 상태 전이는 `draft → pending_verification → production_verified → (deprecated)` 한 방향이 기본이다. `production_verified`에서 값 오류가 발견되면 같은 `dataset_version`을 되돌리지 않고, 수정된 값으로 새 `dataset_version`을 `draft`부터 다시 승격시킨다 (재현성 보존, `06` §8).
5. 데이터셋 로더(§6의 무결성 검사를 통과시키는 컴포넌트)는 승격 시점(`draft→pending_verification`, `pending_verification→production_verified`)을 별도 필드로 남기는 것을 권장한다. 이 문서는 필드 이름을 강제하지 않으나, 강제하는 경우 `status_history` 배열(`{status, at, by}`)을 envelope 확장 필드로 추가할 수 있다.

---

## 4. Canonical ID Reference Convention

`06_ENGINE_CONTRACTS_AND_CORE_RULES.md` §2가 정의한 대로, 천간 ID와 지지 ID는 서로 다른 이름공간이다(`stem:sin` = 辛 ≠ `branch:sin` = 申). 이 문서가 정의하는 모든 데이터셋에서 다른 항목을 가리키는 모든 참조 필드는 다음 규칙을 따른다.

- 천간을 가리키는 값은 항상 `stem:<id>` 형식을 쓴다 (예: `stem:gap`, `stem:sin`).
- 지지를 가리키는 값은 항상 `branch:<id>` 형식을 쓴다 (예: `branch:ja`, `branch:sin`).
- 접두어 없는 bare id(`"sin"`)는 참조 필드에 등장할 수 없다. 등장하면 §6.4 검증 실패로 취급한다.
- `core_tables_v1.json`의 어휘 테이블 자체(예: `heavenly_stems[].id`)는 원래 정의부이므로 접두어를 붙이지 않는다. 접두어 규칙은 **다른 데이터셋이 그 값을 참조할 때**만 적용한다.
- 오행(`element`), 음양(`yin_yang`) 등 stem/branch가 아닌 다른 어휘를 참조할 때는 접두어를 붙이지 않는다(예: `"element": "fire"`). 접두어는 오직 stem/branch id 충돌을 막기 위한 장치다.

이 규칙 하나로 `core_tables_v1.json`의 천간 "신"(辛)과 지지 "신"(申)이 동일 문자열 `"sin"`을 공유하더라도, 이 문서 이후에 추가되는 모든 규칙 데이터셋에서는 어느 쪽을 가리키는지 파일만 봐도 항상 구분된다.

---

## 5. Dataset Schemas

이 절의 각 데이터셋은 §2 envelope을 감싸고, `data` 필드 아래에 아래 구조를 둔다. JSON Schema는 draft-07 스타일로 단순화해 표기했다.

### 5.1 `month_stem_rules_v1` — 오호둔 (연간 → 인월 월간 시작값)

```json
{
  "type": "object",
  "required": ["tiger_start_by_year_stem_group", "month_branch_order_from_in"],
  "properties": {
    "tiger_start_by_year_stem_group": {
      "type": "array",
      "minItems": 5,
      "maxItems": 5,
      "items": {
        "type": "object",
        "required": ["year_stems", "in_month_start_stem"],
        "properties": {
          "year_stems": {
            "type": "array",
            "minItems": 2, "maxItems": 2,
            "items": {"type": "string", "pattern": "^stem:"}
          },
          "in_month_start_stem": {"type": "string", "pattern": "^stem:"}
        }
      }
    },
    "month_branch_order_from_in": {
      "type": "array",
      "minItems": 12, "maxItems": 12,
      "items": {"type": "string", "pattern": "^branch:"}
    }
  }
}
```

예시 데이터 (06 §3.1 표를 그대로 옮긴 것):

```json
{
  "tiger_start_by_year_stem_group": [
    {"year_stems": ["stem:gap", "stem:gi"], "in_month_start_stem": "stem:byeong"},
    {"year_stems": ["stem:eul", "stem:gyeong"], "in_month_start_stem": "stem:mu"},
    {"year_stems": ["stem:byeong", "stem:sin"], "in_month_start_stem": "stem:gyeong"},
    {"year_stems": ["stem:jeong", "stem:im"], "in_month_start_stem": "stem:im"},
    {"year_stems": ["stem:mu", "stem:gye"], "in_month_start_stem": "stem:gap"}
  ],
  "month_branch_order_from_in": [
    "branch:in", "branch:myo", "branch:jin", "branch:sa", "branch:o", "branch:mi",
    "branch:sin", "branch:yu", "branch:sul", "branch:hae", "branch:ja", "branch:chuk"
  ]
}
```

검증 규칙:

- `tiger_start_by_year_stem_group`의 `year_stems`를 모두 펼치면 천간 10개가 정확히 한 번씩만 나와야 한다 (중복·누락 금지).
- `month_branch_order_from_in`은 지지 12개가 정확히 한 번씩, `branch:in`부터 시작해야 한다.
- 월간 계산은 `month_stem_index = (stem_index(in_month_start_stem) + index_of(target_branch, month_branch_order_from_in)) mod 10`으로 재현 가능해야 한다. 검증 시 위 5개 그룹 × 12개 월지 = 60개 조합을 모두 계산해 표에 이미 알려진 어떤 값과도 모순되지 않는지 회귀 테스트로 확인한다(초기 버전은 표가 곧 정답이므로 자기 일관성 검사가 된다).

### 5.2 `hour_stem_rules_v1` — 오서둔 (일간 → 자시 시간 시작값)

```json
{
  "type": "object",
  "required": ["rat_start_by_day_stem_group", "hour_branch_order_from_ja"],
  "properties": {
    "rat_start_by_day_stem_group": {
      "type": "array",
      "minItems": 5, "maxItems": 5,
      "items": {
        "type": "object",
        "required": ["day_stems", "ja_hour_start_stem"],
        "properties": {
          "day_stems": {
            "type": "array", "minItems": 2, "maxItems": 2,
            "items": {"type": "string", "pattern": "^stem:"}
          },
          "ja_hour_start_stem": {"type": "string", "pattern": "^stem:"}
        }
      }
    },
    "hour_branch_order_from_ja": {
      "type": "array",
      "minItems": 12, "maxItems": 12,
      "items": {"type": "string", "pattern": "^branch:"}
    }
  }
}
```

예시 데이터 (06 §3.2 표):

```json
{
  "rat_start_by_day_stem_group": [
    {"day_stems": ["stem:gap", "stem:gi"], "ja_hour_start_stem": "stem:gap"},
    {"day_stems": ["stem:eul", "stem:gyeong"], "ja_hour_start_stem": "stem:byeong"},
    {"day_stems": ["stem:byeong", "stem:sin"], "ja_hour_start_stem": "stem:mu"},
    {"day_stems": ["stem:jeong", "stem:im"], "ja_hour_start_stem": "stem:gyeong"},
    {"day_stems": ["stem:mu", "stem:gye"], "ja_hour_start_stem": "stem:im"}
  ],
  "hour_branch_order_from_ja": [
    "branch:ja", "branch:chuk", "branch:in", "branch:myo", "branch:jin", "branch:sa",
    "branch:o", "branch:mi", "branch:sin", "branch:yu", "branch:sul", "branch:hae"
  ]
}
```

검증 규칙:

- `day_stems`를 모두 펼치면 천간 10개가 정확히 한 번씩 나온다.
- `hour_branch_order_from_ja`는 지지 12개가 정확히 한 번씩, `branch:ja`부터 시작한다.
- 이 데이터셋은 시지 자체를 정하지 않는다. 시지는 `core_tables_v1.json`의 `hour_branch_windows_legal_local_time`과 Calculation Profile의 `time_basis`로 이미 정해진 값을 입력으로 받는다 — 이 데이터셋과 시지 판정 로직을 같은 파일에 두지 않는다.

### 5.3 `ten_gods_v1` — 십신 산출표

```json
{
  "type": "object",
  "required": ["relation_table", "polarity_rule", "display_names"],
  "properties": {
    "relation_table": {
      "type": "array",
      "minItems": 5, "maxItems": 5,
      "items": {
        "type": "object",
        "required": ["relation_element", "same_polarity", "different_polarity"],
        "properties": {
          "relation_element": {
            "type": "string",
            "enum": [
              "same_element",
              "day_master_generates_target",
              "day_master_controls_target",
              "target_controls_day_master",
              "target_generates_day_master"
            ]
          },
          "same_polarity": {"type": "string"},
          "different_polarity": {"type": "string"}
        }
      }
    },
    "polarity_rule": {
      "type": "string",
      "description": "yin_yang 값이 같으면 same_polarity, 다르면 different_polarity를 선택한다는 것을 명시하는 고정 문자열.",
      "const": "same_yin_yang_selects_same_polarity_column"
    },
    "display_names": {
      "type": "object",
      "description": "ten_god id → 표시용 한글/한자. Interpretation 문구가 아니라 명칭 표기이므로 이 데이터셋에 둔다.",
      "additionalProperties": {
        "type": "object",
        "required": ["korean", "hanja"],
        "properties": {"korean": {"type": "string"}, "hanja": {"type": "string"}}
      }
    }
  }
}
```

예시 데이터 (06 §5.2 표):

```json
{
  "relation_table": [
    {"relation_element": "same_element", "same_polarity": "bigyeon", "different_polarity": "geopjae"},
    {"relation_element": "day_master_generates_target", "same_polarity": "siksin", "different_polarity": "sangwan"},
    {"relation_element": "day_master_controls_target", "same_polarity": "pyeonjae", "different_polarity": "jeongjae"},
    {"relation_element": "target_controls_day_master", "same_polarity": "pyeongwan", "different_polarity": "jeonggwan"},
    {"relation_element": "target_generates_day_master", "same_polarity": "pyeonin", "different_polarity": "jeongin"}
  ],
  "polarity_rule": "same_yin_yang_selects_same_polarity_column",
  "display_names": {
    "bigyeon": {"korean": "비견", "hanja": "比肩"},
    "geopjae": {"korean": "겁재", "hanja": "劫財"},
    "siksin": {"korean": "식신", "hanja": "食神"},
    "sangwan": {"korean": "상관", "hanja": "傷官"},
    "pyeonjae": {"korean": "편재", "hanja": "偏財"},
    "jeongjae": {"korean": "정재", "hanja": "正財"},
    "pyeongwan": {"korean": "편관", "hanja": "偏官"},
    "jeonggwan": {"korean": "정관", "hanja": "正官"},
    "pyeonin": {"korean": "편인", "hanja": "偏印"},
    "jeongin": {"korean": "정인", "hanja": "正印"}
  }
}
```

검증 규칙:

- `relation_table`은 `relation_element` enum 5개 값이 각각 정확히 한 번씩 등장해야 한다.
- `same_polarity`/`different_polarity`에 쓰인 ten_god id 10개는 서로 달라야 하며(총 10개), `display_names`에 정의된 키 집합과 정확히 일치해야 한다.
- 이 데이터셋은 오행 생극 방향(`06` §5.1: `wood→fire→earth→metal→water→wood` 등)을 별도로 포함하지 않는다. `relation_element`를 판정하는 것은 엔진 로직(오행 생극표 참조)의 책임이고, 이 데이터셋은 판정 결과를 십신 이름에 매핑하는 표에 한정한다.
- 십신은 일간과 **천간**의 관계로만 산출한다(`06` §5.2). 이 데이터셋에 지지 자체의 십신 매핑을 추가하지 않는다.

### 5.4 `hidden_stems_v1` — 지장간

```json
{
  "type": "object",
  "required": ["branch_hidden_stems"],
  "properties": {
    "branch_hidden_stems": {
      "type": "object",
      "description": "지지 12개를 key로 갖는 객체. key는 branch: 접두어를 포함한다.",
      "propertyNames": {"pattern": "^branch:"},
      "additionalProperties": {
        "type": "array",
        "minItems": 1, "maxItems": 3,
        "items": {
          "type": "object",
          "required": ["stem", "role", "display_order"],
          "properties": {
            "stem": {"type": "string", "pattern": "^stem:"},
            "role": {"type": "string", "enum": ["main", "middle", "residual"]},
            "display_order": {"type": "integer", "minimum": 1}
          }
        }
      }
    }
  }
}
```

예시 데이터 (06 §5.3 표, 일부 발췌):

```json
{
  "branch_hidden_stems": {
    "branch:ja": [{"stem": "stem:gye", "role": "main", "display_order": 1}],
    "branch:chuk": [
      {"stem": "stem:gi", "role": "main", "display_order": 1},
      {"stem": "stem:gye", "role": "middle", "display_order": 2},
      {"stem": "stem:sin", "role": "residual", "display_order": 3}
    ],
    "branch:in": [
      {"stem": "stem:gap", "role": "main", "display_order": 1},
      {"stem": "stem:byeong", "role": "middle", "display_order": 2},
      {"stem": "stem:mu", "role": "residual", "display_order": 3}
    ]
  }
}
```

검증 규칙:

- `branch_hidden_stems`는 지지 12개 키를 모두 포함해야 한다(`branch:ja` … `branch:hae`).
- 각 지지 배열에는 `role: "main"`이 정확히 하나 있어야 한다.
- 같은 지지 배열 안에서 `display_order`는 1부터 시작하는 연속 정수이며 중복이 없어야 한다.
- 가중치, 계절 강약, 투간 여부 등 해석/강약 판단에 쓰이는 필드는 이 스키마에 추가하지 않는다(`06` §5.3 명시 사항).

### 5.5 `relations_v1` — 합·충·형·파·해

```json
{
  "type": "object",
  "required": ["stem_combinations", "branch_relations"],
  "properties": {
    "stem_combinations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["relation_id", "relation_type", "participants", "resulting_element"],
        "properties": {
          "relation_id": {"type": "string"},
          "relation_type": {"const": "stem_combination"},
          "participants": {
            "type": "array", "minItems": 2, "maxItems": 2,
            "items": {"type": "string", "pattern": "^stem:"}
          },
          "resulting_element": {
            "type": "string",
            "enum": ["wood", "fire", "earth", "metal", "water"]
          }
        }
      }
    },
    "branch_relations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["relation_id", "relation_type", "participants"],
        "properties": {
          "relation_id": {"type": "string"},
          "relation_type": {
            "type": "string",
            "enum": [
              "branch_six_combination",
              "branch_three_harmony",
              "branch_half_three_harmony_candidate",
              "branch_clash",
              "branch_punishment",
              "branch_self_punishment",
              "branch_break",
              "branch_harm"
            ]
          },
          "participants": {
            "type": "array", "minItems": 2, "maxItems": 3,
            "items": {"type": "string", "pattern": "^branch:"}
          },
          "resulting_element": {
            "type": "string",
            "enum": ["wood", "fire", "earth", "metal", "water"],
            "description": "육합·삼합처럼 결과 오행이 있는 관계에만 존재. 충·형·파·해에는 두지 않는다."
          }
        }
      }
    }
  }
}
```

예시 데이터 (구조 예시 — 전체 조합표는 §5.5 하단 "완결성 요구사항" 참고):

```json
{
  "stem_combinations": [
    {"relation_id": "stem-comb-gap-gi", "relation_type": "stem_combination",
     "participants": ["stem:gap", "stem:gi"], "resulting_element": "earth"}
  ],
  "branch_relations": [
    {"relation_id": "branch-yukhap-ja-chuk", "relation_type": "branch_six_combination",
     "participants": ["branch:ja", "branch:chuk"], "resulting_element": "earth"},
    {"relation_id": "branch-samhap-in-o-sul", "relation_type": "branch_three_harmony",
     "participants": ["branch:in", "branch:o", "branch:sul"], "resulting_element": "fire"},
    {"relation_id": "branch-half-samhap-in-o", "relation_type": "branch_half_three_harmony_candidate",
     "participants": ["branch:in", "branch:o"], "resulting_element": "fire"},
    {"relation_id": "branch-chung-ja-o", "relation_type": "branch_clash",
     "participants": ["branch:ja", "branch:o"]}
  ]
}
```

검증 규칙:

- `relation_id`는 파일 전체에서 유일해야 한다.
- `stem_combination`의 `participants`는 서로 다른 두 천간이어야 한다. 천간합 5쌍(갑기, 을경, 병신, 정임, 무계) 전부가 존재해야 완결된 것으로 간주한다.
- `branch_three_harmony`는 세 지지가 모두 있는 조합만 이 타입으로 등록한다. 두 지지만 확인된 경우는 반드시 `branch_half_three_harmony_candidate`로 별도 등록하고, `branch_three_harmony`로 승격하지 않는다(`06` §5.4).
- `branch_clash`, `branch_punishment`, `branch_self_punishment`, `branch_break`, `branch_harm`에는 `resulting_element`를 넣지 않는다(포함되어 있으면 검증 실패).
- `branch_self_punishment`(자형)는 같은 지지가 두 개 이상 등장하는 조합에만 정의한다. 이 데이터셋 자체는 "어느 pillar 위치의 지지끼리 비교하는지"를 정하지 않는다 — 그 판정은 엔진이 원국의 실제 pillar 조합에 이 표를 적용할 때 수행한다(`06` §5.4).
- **완결성 요구사항**: `production_verified`로 승격하려면 최소한 다음을 모두 포함해야 한다 — 천간합 5쌍, 지지 육합 6쌍, 지지 삼합 4조(및 그에 대응하는 반합 후보 조합), 지지 충 6쌍. 형·파·해는 전통별로 구성이 다를 수 있으므로, 이 문서는 어떤 형·파·해 조합표를 채택할지 결정하지 않는다 — 채택한 조합표의 출처(예: 특정 문헌)를 `source`에 명시하고 팀 검토를 거친 뒤 `pending_verification`으로 등록한다.

---

## 6. Data Integrity Checks

모든 데이터셋 로더(또는 CI lint 스크립트)는 다음을 공통으로 검사한다.

### 6.1 필수 항목

- §2 envelope 필드 7종이 모두 존재하고 타입이 올바른가.
- `status`가 §3의 4개 값 중 하나인가.
- 각 데이터셋의 `data`가 §5(또는 §8)의 필수 필드를 모두 포함하는가.

### 6.2 중복

- 같은 논리적 항목(예: 천간 10개, 지지 12개, 십신 10개, `relation_id`)이 파일 안에서 중복 정의되지 않았는가.
- 서로 다른 `dataset_id`가 같은 규칙 영역(예: 월간 규칙)을 동시에 `production_verified` 상태로 갖고 있지 않은가 — 오직 하나의 production 데이터셋만 특정 계산 영역을 대표해야 한다.

### 6.3 순서

- 순서가 의미를 갖는 배열(`month_branch_order_from_in`, `hour_branch_order_from_ja`, 지장간의 `display_order`)이 정의된 순환/서열을 지키는가.
- `display_order`처럼 정수 순서를 쓰는 필드는 1부터 연속인가(건너뜀 금지).

### 6.4 참조 무결성

- 모든 `stem:` 참조는 `core_tables_v1.json`의 `heavenly_stems[].id`에 존재하는 id를 가리키는가.
- 모든 `branch:` 참조는 `core_tables_v1.json`의 `earthly_branches[].id`에 존재하는 id를 가리키는가.
- 접두어 없는 bare id가 참조 필드에 남아 있지 않은가(§4).
- `ten_gods_v1.display_names`의 키 집합과 `relation_table`이 참조하는 ten_god id 집합이 정확히 일치하는가.

### 6.5 Production 상태 게이트

- `status: "production_verified"`인 데이터셋은 §3.1의 승격 조건(독립 검증, 팀 승인 등 — 데이터셋 종류별 세부 절차는 이 문서 범위 밖이며 `04`/`05`/`06`이 정의한 게이트를 따른다)을 통과했다는 근거가 `source` 또는 별도 검토 기록에 남아 있는가.
- production 계산 경로가 실제로 `draft`/`pending_verification` 데이터셋을 로드하려는 시도를 전부 차단하고 `DATASET_NOT_PRODUCTION_VERIFIED`로 귀결되는가(코드 레벨 강제는 이 문서가 아니라 구현 단계의 책임이지만, lint는 데이터 쪽에서 상태 표기가 정확한지까지만 검사한다).

이 검사들은 CI에서 매 커밋마다 실행할 수 있는 정적 검사이며, 천문/역사 데이터 자체의 사실 정확성(§8)은 별도 검증 절차의 몫이다.

---

## 7. Fixture and Production Data Separation

- Production 후보 데이터는 `data/saju/`에 두고, 회귀 테스트 fixture는 기존 관례대로 `tests/fixtures/saju/`에 둔다. 두 위치의 데이터는 서로 다른 목적을 가지며 서로를 대체하지 않는다.
- `tests/fixtures/saju/*.json`의 각 fixture는 "입력 + 기대 출력" 쌍이며, §2의 계산 데이터셋 envelope과는 다른 스키마(이미 `tests/fixtures/saju/README.md`가 정의)를 따른다. 이 문서가 정의하는 envelope을 fixture 파일에 강제하지 않는다.
- fixture가 특정 계산 데이터셋 버전을 전제로 한다면(예: `calculation_profile_id`), 그 fixture는 자신이 어떤 `dataset_id`/`dataset_version`을 기준으로 기대값을 계산했는지 `evidence`/`evidence_ref` 필드에 남긴다(`tests/fixtures/saju/README.md`의 기존 관례를 따른다).
- **fixture 데이터는 production 계산 경로에 로드될 수 없다.** production 로더는 `data/saju/`의 `production_verified` 데이터셋만 참조하며, `tests/fixtures/saju/` 경로 자체를 알지 못하는 것이 이상적이다(적어도 참조하지 않아야 한다).
- 반대로 `data/saju/`에 있는 `draft`/`pending_verification` 데이터셋을 fixture의 "기대값 정답"으로 그대로 베끼지 않는다. fixture의 기대값은 독립적으로 근거가 있어야 하며, 같은 초안 데이터를 그대로 복사해 자기 자신을 검증하는 순환 검증을 피한다(`tests/fixtures/saju/README.md`가 이미 명시한 "테스트를 통과시키기 위해 기대값을 맞추지 않는다" 원칙과 동일).

---

## 8. Pending Rule Data — Schema Stance Only

다음 세 영역은 아직 실제 값이 확정되지 않았다. 이 문서는 **이 값들을 정의하지 않으며**, 향후 이 값들을 담을 데이터셋도 §2 envelope과 §3 status enum을 동일하게 따라야 한다는 것만 규정한다.

### 8.1 절입시각 (Solar-term instants)

- 향후 `dataset_id: solar_term_instants_v1`(가칭)로 제공될 것이며, `05_CALCULATION_DATA_SOURCES.md` §1이 요구하는 천문 모델·생성 스크립트·오차 정책을 `source`에 기록해야 한다.
- 이 데이터셋은 실제 절입시각 값이 채워지기 전까지 `status: draft` 이상으로 올라갈 수 없다.
- 이 문서는 절입시각의 어떤 예시값도 제시하지 않는다.

### 8.2 일주 anchor (Day-pillar anchor)

- 기존 `data/saju/day_pillar_anchor_candidates_v1.json`이 이미 이 영역의 "보류 데이터셋" 패턴을 보여준다 — `status: "not_for_production"`(§3의 `draft`/`pending_verification`에 대응), 단일 출처만 확보된 상태(`verification_status: "single_source_only"`), 그리고 `promotion_gate`에 승격 조건을 명시.
- 향후 이 후보가 §2 envelope으로 정리될 때도 동일한 원칙을 유지한다: 독립된 두 번째 출처와 60일 회귀 세트를 확보하기 전에는 `status`를 `production_verified`로 올리지 않는다(`04` §11, `05` §2, §4).
- 이 문서는 anchor 날짜나 JDN 값을 새로 제시하거나 확정하지 않는다.

### 8.3 대운 규칙 (Daewoon rules)

- `06_ENGINE_CONTRACTS_AND_CORE_RULES.md` §9가 이미 `kr_standard_v1`에서 대운 순역·기산 규칙을 명시적으로 미확정 상태로 남겼다.
- 향후 `dataset_id: daewoon_rules_v1`(가칭)이 만들어지더라도, 성별 규칙·순역 판정·절입 기준·기산 환산 방식이 팀 승인을 받기 전까지는 `status: draft`를 넘지 않는다.
- 이 문서는 대운 방향이나 기산 공식의 어떤 구체값도 제시하지 않는다.

이 세 영역에 대해 지금 시점에 필요한 구현 작업은 "값을 채우는 것"이 아니라, 값이 확정됐을 때 곧바로 §2~§3 형식에 맞춰 넣을 수 있도록 그 자리를 비워두고 `blocked`/`DAEWOON_RULE_NOT_CONFIGURED`/`SOLAR_TERM_DATA_UNAVAILABLE`/`DAY_PILLAR_ANCHOR_UNAVAILABLE` 코드로 정직하게 표시하는 것이다(`06` §7).

---

## 9. Versioning Cross-reference

이 문서가 정의한 `dataset_version` 증가 규칙은 `06_ENGINE_CONTRACTS_AND_CORE_RULES.md` §8과 동일하다. 요약:

- 값·알고리즘·출처가 계산 결과를 바꾸는 변경 → `dataset_version`의 major 증가.
- 이 문서(§2, §5)가 정의하는 필드 구조 자체가 바뀌는 변경 → 해당 데이터셋의 `schema_version` 증가.
- 데이터셋 내용은 그대로인데 이를 소비하는 엔진 코드만 바뀌어 같은 입력의 결과가 달라질 수 있게 되면 → `engine_version` 증가와 경계 회귀 테스트 재실행(코드 관점이므로 이 문서 범위 밖이나, 데이터셋 쪽에서는 `dataset_version`을 올리지 않아야 한다는 점만 확인한다).

---

## 10. Open Items

1. §5.5 `relations_v1`의 형·파·해 조합표를 어느 문헌/전통 기준으로 채택할지 결정 및 팀 승인.
2. §3.1의 "승격 근거 기록" 방식(예: `status_history` 필드 채택 여부, 또는 별도 승인 로그 문서/PR 링크 방식)을 확정.
3. §6의 무결성 검사를 실제 lint 스크립트로 구현할 때 사용할 언어/도구 선택(코드 작성은 이 문서의 범위 밖).
4. §8의 세 보류 영역 각각에 대해 `dataset_id` 가칭을 정식 이름으로 확정.
