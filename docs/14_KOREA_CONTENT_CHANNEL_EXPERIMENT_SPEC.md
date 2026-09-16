# Destiny — Korea Content Channel Experiment Specification

> Status: pre-launch experiment design. This does not create accounts, publish
> content, spend advertising budget, or collect user data.

## 1. Goal

Identify which early content format earns meaningful voluntary interest in a
Korea-focused Saju MVP. This experiment does not claim that one channel is
universally best, nor does it measure product conversion before a product
entry point exists.

## 2. First experiment portfolio

| Channel | Format | User need tested | Role |
| --- | --- | --- | --- |
| Naver Blog | searchable explanatory post | “I want a clear answer before trying a service.” | Durable search-intent content. |
| Instagram | vertical Reel | “Show me a useful idea quickly.” | New-audience discovery. |
| Instagram | carousel / illustrated short comic | “Explain it simply enough to save or share.” | Comprehension and shareability. |

Google Blogger and YouTube Shorts are **second-wave candidates**. They are not
discarded; omitting them in the first run keeps creation capacity focused and
the comparison interpretable.

## 3. Shared editorial position

Every format starts from the same factual, user-helpful topic. The first three
topics are:

1. `출생시간을 몰라도 사주를 볼 수 있나요?` — explain the three-pillar
   result and what is excluded.
2. `밤 11시 이후 출생이라면 무엇이 달라질 수 있나요?` — explain that a
   date-boundary convention can change a result, without saying one convention
   is universally correct.
3. `사주 계산에서 AI가 하는 일과 하지 않는 일` — explain that the engine
   calculates structured facts and AI only helps interpret them.

No content may promise a future outcome, diagnose a problem, give investment,
legal, medical, or safety advice, claim a calculation is infallible, or imply
that a viewer's hidden personal facts are known.

## 4. Content adaptation rules

| Asset | Naver Blog | Reel | Carousel / webtoon |
| --- | --- | --- | --- |
| Core claim | Full explanation, examples, limits, and a source/FAQ link. | One clear question, one answer, one limit. | One question across 5–7 cards, ending with the limit and next step. |
| Length | 700–1,200 Korean words initially. | 20–35 seconds. | 5–7 cards with concise Korean copy. |
| Call to action | “베타 소식 받기” or “계산 방식 알아보기.” | Same CTA in caption/profile link. | Same CTA on final card/caption. |
| Accessibility | headings, plain language, descriptive image alt text where supported. | Korean captions embedded or supplied. | legible text, no colour-only meaning, image description where supported. |

The underlying factual script, CTA wording, and destination must be the same
for all three variants of a topic. Format—not a changed promise—is what the
experiment compares.

## 5. Measurement plan

### 5.1 Primary signals

| Signal | Definition | Interpretation |
| --- | --- | --- |
| Qualified destination visit | voluntary visit to the shared landing/interest page with channel and format tag | Stronger than a view; still not product demand. |
| Voluntary beta-interest action | explicit opt-in or request for an update after seeing the notice | Earliest intent signal; requires a separate privacy-approved collection flow. |
| Save/share rate | saves or shares divided by platform reach where platform data permits | Indicates utility or social relevance, not conversion. |
| Completion/read-through | Reel completion or blog/carousel consumption indicator available from the platform | Indicates format comprehension. |

### 5.2 Guardrails

- Do not compare raw views across channels as if they were equal.
- Do not purchase followers, use engagement pods, or conceal promotional
  material as personal advice.
- Do not collect birth data in a channel comment, direct message, or generic
  analytics event.
- Do not use a waitlist form until consent text, retention, contact method,
  deletion path, and access controls are approved.
- Measure production time per asset so a small apparent reach gain does not
  hide an unsustainable content cost.

## 6. Cold-start account policy

All currently available social accounts may begin with no followers. This is
not a failure and must not be treated as a like-for-like reach comparison with
an established creator account.

The first run answers only:

- which explanation earns a meaningful action from the small audience the
  platform actually reaches;
- which format can be produced consistently and understood correctly;
- whether the public profile and content promise are clear enough to retain
  an interested visitor.

It does **not** choose a permanent channel winner from early raw views,
follower count, or one unusually distributed post. Naver Blog also has a
different discovery cycle from social feeds, so it must not be judged on the
same two-week exposure window.

Before publishing experiments, complete a small profile baseline on every
active account:

1. A consistent display name, profile image, one-sentence purpose, and a
   contact/landing destination.
2. Clear disclosure that the service is under development; no promise that a
   beta, reading, or launch date already exists.
3. One pinned or otherwise visible introduction explaining what Destiny
   calculates, what AI does not calculate, and the interpretation/safety
   boundary.

Do not buy followers or run engagement exchanges to escape the cold start;
they contaminate the experiment and create misleading audience signals.

## 7. Run design

Start with a two-stage organic pilot:

**Stage A — profile baseline (7–10 days):** establish the profile baseline and
publish the first shared topic in all relevant formats. Record only operational
issues and comprehension feedback; do not select a channel winner.

**Stage B — content comparison (four weeks after Stage A):** publish the
remaining topics and compare qualified action, consumption, saves/shares, and
production cost within each channel. Keep the factual script and CTA aligned.

The initial content plan is:

- three shared topics;
- one Naver Blog post and one Instagram carousel per topic;
- one vertical short video per topic, distributed unchanged to Instagram Reels
  and TikTok; Facebook receives the same Reel as a secondary distribution
  surface;
- publish at broadly comparable times where feasible, but record the actual
  time rather than assuming it is equivalent across platforms;
- no paid amplification in the first run;
- retain post URLs, publication time, content/script version, and CTA version.

This is nine original content assets (three articles, three carousels, and
three videos), with the videos distributed to multiple short-form surfaces.
If capacity is limited, begin with the first topic in all formats before
making more. Do not judge a channel from one post.

## 8. Review and next decision

At the end of the observation window, record for every asset:

- reach/impressions and platform-specific consumption metric;
- saves/shares/comments, with spam removed under a documented rule;
- qualified destination visits and approved opt-ins, if implemented;
- production time and material cost;
- qualitative feedback, separated from personal data.

Select the next-wave channel only if it improves a primary signal without a
material safety, privacy, or operational-cost problem. For new accounts,
require repeated evidence across multiple assets rather than a single
high-reach post. Otherwise keep the result as `inconclusive` and run a revised
topic or format.

## 9. Required approvals before execution

Before publishing the first asset, a product owner must approve:

1. Brand/account ownership and public-profile wording.
2. Final factual scripts and their sources.
3. Landing page and CTA destination.
4. Beta-interest collection/privacy notice, if any.
5. Comment and direct-message moderation policy.
6. Who may publish, respond publicly, or escalate a harmful comment.

Content publication is representational communication. It is deliberately out
of scope for this repository-only specification.
