# Destiny — Naver Blog Launch Kit

> Draft only. Requires product-owner approval before public posting.
> The posts describe product principles; they do not promise a launch date,
> beta access, or completed user-facing service.

## 1. Profile setup

### Recommended blog title

`Destiny | 사주를 정확하게 계산하는 기록`

### One-line introduction

`출생정보와 절기 기준을 바탕으로, 이해하기 쉬운 사주 계산을 만들고 기록합니다.`

### Suggested categories

1. `Destiny 소개`
2. `사주 계산 이야기`
3. `출생정보 안내`
4. `개발 기록`
5. `자주 묻는 질문`

Do not add “무료 사주”, “정확도 100%”, “신점”, “재회 보장”, or similar
search-attracting claims to the title, profile, category names, or tags.

## 2. Publishing order

| Order | Title | Category | Purpose |
| --- | --- | --- | --- |
| 1 | `Destiny는 무엇을 만들고 있나요?` | Destiny 소개 | Explain the project’s boundary and build trust. |
| 2 | `출생시간을 모르면 사주를 볼 수 없을까요?` | 출생정보 안내 | Give a concrete, helpful answer to a common concern. |
| 3 | `밤 11시 이후 출생이라면, 왜 계산 기준이 달라질 수 있을까요?` | 사주 계산 이야기 | Explain a meaningful calculation difference without jargon-first teaching. |

Publish one post at a time and leave space for proofreading and comments.
Do not release all three as an artificial content burst.

## 3. Post 1 draft

### Destiny는 무엇을 만들고 있나요?

사주를 처음 접하면 가장 먼저 이런 생각이 들 수 있습니다.

`내가 알고 있는 출생정보만으로도 계산할 수 있을까?`

`출생시간을 정확히 모르는데 괜찮을까?`

`결과마다 왜 조금씩 다르게 보일까?`

Destiny는 이 질문에서 출발하고 있습니다. 출생정보와 절기 기준을 바탕으로 사주 계산의 구조를 분명하게 보여 주고, 어려운 용어는 가능한 쉬운 말로 풀어 주는 것을 목표로 합니다.

사주 계산에는 출생 날짜뿐 아니라 출생시간, 날짜가 바뀌는 기준, 절기 같은 요소가 영향을 줄 수 있습니다. 그래서 Destiny는 모르는 정보를 임의로 채우지 않으려 합니다. 출생시간을 모르면 그 사실을 결과에 남기고, 계산할 수 있는 범위와 아직 포함할 수 없는 범위를 구분해서 보여 주는 방식입니다.

또 하나의 원칙은 계산과 해석을 구분하는 것입니다. 사주 구조 자체는 정해진 규칙과 데이터로 계산하고, 해석은 그 결과를 바탕으로 이해를 돕는 참고 자료로 제공합니다. AI가 계산값을 마음대로 만들어 내거나 바꾸지 않도록 설계하는 이유도 여기에 있습니다.

Destiny는 아직 개발 중입니다. 이 블로그에서는 사주 계산에 필요한 출생정보, 계산 기준이 달라질 수 있는 경우, 그리고 서비스를 만들어 가는 과정을 차근차근 기록하겠습니다.

사주는 미래를 단정하는 답이 아니라, 자신을 돌아보고 생각을 정리하는 하나의 참고가 될 수 있다고 생각합니다.

**추천 태그:** `#Destiny #사주계산 #사주 #출생정보 #개발기록`

## 4. Post 2 draft

### 출생시간을 모르면 사주를 볼 수 없을까요?

결론부터 말하면, 출생시간을 모른다고 해서 사주를 전혀 볼 수 없는 것은 아닙니다.

사주는 보통 연주, 월주, 일주, 시주의 네 가지 기둥으로 설명합니다. 이 가운데 출생시간이 없으면 시주는 계산할 수 없지만, 출생 날짜가 확인되면 연주·월주·일주까지는 계산할 수 있는 경우가 있습니다.

그래서 중요한 것은 모르는 시간을 억지로 정하는 것이 아닙니다. 예를 들어 출생시간을 모르는데 자정이나 정오로 임의 입력하면, 실제와 다른 시주가 만들어질 수 있습니다.

Destiny는 출생시간이 없을 때 이렇게 다루려 합니다.

1. 출생 날짜로 계산 가능한 부분을 먼저 보여 줍니다.
2. 시주와 시주를 전제로 하는 설명은 포함하지 않았다고 알려 줍니다.
3. 나중에 출생시간을 확인하면 새 계산 기준으로 다시 볼 수 있게 합니다.

시간을 대략적으로만 아는 경우에도 마찬가지입니다. “새벽쯤이었다”처럼 정확한 시각을 모른다면, 확실하지 않은 부분을 확실한 것처럼 말하지 않는 편이 더 정직합니다.

출생시간을 모른다는 것은 잘못된 입력이 아닙니다. 알고 있는 사실만으로 계산하고, 모르는 부분은 모른다고 남기는 것이 더 신뢰할 수 있는 출발점이라고 생각합니다.

**추천 태그:** `#출생시간 #사주초보 #사주계산 #사주보는법 #Destiny`

## 5. Post 3 draft

### 밤 11시 이후 출생이라면, 왜 계산 기준이 달라질 수 있을까요?

밤 11시 이후에 태어났다는 기록이 있다면, “날짜는 다음 날로 봐야 할까?”라는 질문이 생길 수 있습니다.

사주 계산에서는 날짜가 바뀌는 기준을 자정으로 보는 방식과, 자시가 시작되는 밤 11시부터 다음 날로 보는 방식이 함께 사용됩니다. 그래서 밤 11시부터 자정 사이 출생 기록은 어떤 기준을 적용하느냐에 따라 일주가 달라질 수 있습니다.

이 차이는 입력이 틀렸다는 뜻이 아닙니다. 서로 다른 계산 약속이 존재한다는 뜻입니다.

Destiny의 기본 계산은 하나의 기준을 명시해서 사용합니다. 그리고 다른 지원 기준으로 계산했을 때 실제 사주 구조가 달라지는 경우에만, 사용자가 두 결과를 비교할 수 있게 하려 합니다. 차이가 없는데도 어려운 선택을 먼저 요구하지는 않습니다.

중요한 것은 어떤 기준이 “언제나 유일하게 맞다”고 단정하는 것이 아니라, 어떤 기준을 사용했는지 결과와 함께 남기는 일입니다. 그래야 같은 출생정보를 나중에 다시 계산해도 왜 결과가 나왔는지 확인할 수 있습니다.

처음에는 낯선 내용일 수 있지만, 사용자가 알아야 할 때만 쉬운 말로 설명하는 것이 Destiny가 지키려는 원칙입니다.

**추천 태그:** `#자시 #출생시간 #사주계산 #사주기준 #Destiny`

## 6. Visual and comment guidance

- Use one simple original diagram or plain text card per post; do not use a
  stock “mystical prediction” image as the main claim.
- Do not use a person’s birth data as an example unless it is synthetic or
  explicitly authorised.
- Reply to comments with general explanation only. Do not calculate a
  commenter’s Saju in public comments or request birth data there.
- For requests involving health, law, finance, safety, or a relationship
  decision, restate the informational boundary rather than giving personal
  advice.

## 7. Before-publish checklist

- [ ] Profile shows Destiny-only purpose and no residual mystery branding.
- [ ] Every factual statement matches the calculation specifications.
- [ ] No launch date, free-reading availability, or outcome guarantee appears.
- [ ] The title, cover image, and tags match the article rather than a
      high-traffic unrelated query.
- [ ] A human reviewed Korean wording, links, and image rights.
- [ ] The exact published text, image source, date, and CTA version are logged
      for the channel experiment.
