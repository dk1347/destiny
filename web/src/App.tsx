import { FormEvent, useState } from "react";

type Pillar = { stem: string; branch: string };
type SajuResult = { pillars: Record<string, Pillar>; warnings: string[] };
type Relation = { relation_id: string; relation_type: string; participants: string[]; resulting_element?: string | null };
type SeunResult = { calendar_year: number; pillar: Pillar; relations: Relation[] };

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
const stemLabels: Record<string, string> = { gap: "갑", eul: "을", byeong: "병", jeong: "정", mu: "무", gi: "기", gyeong: "경", sin: "신", im: "임", gye: "계" };
const branchLabels: Record<string, string> = { ja: "자", chuk: "축", in: "인", myo: "묘", jin: "진", sa: "사", o: "오", mi: "미", sin: "신", yu: "유", sul: "술", hae: "해" };
const relationLabels: Record<string, string> = {
  stem_combination: "천간합", branch_six_combination: "지지 육합", branch_three_harmony: "삼합",
  branch_half_three_harmony_candidate: "반삼합 후보", branch_clash: "충",
};
const elementLabels: Record<string, string> = { wood: "목", fire: "화", earth: "토", metal: "금", water: "수" };
const locationLabels: Record<string, string> = {
  year_stem: "연간", month_stem: "월간", day_stem: "일간", hour_stem: "시간", seun_stem: "세운 천간",
  year_branch: "연지", month_branch: "월지", day_branch: "일지", hour_branch: "시지", seun_branch: "세운 지지",
};

function koreanPillar(pillar: Pillar) { return `${stemLabels[pillar.stem]}${branchLabels[pillar.branch]}`; }
function kstIso(date: string, time: string) { return `${date}T${time}:00+09:00`; }
function annualRelations(relations: Relation[]) {
  return relations.filter((relation) => relation.participants.some((location) => location === "seun_stem" || location === "seun_branch"));
}

export default function App() {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [result, setResult] = useState<SajuResult>();
  const [annual, setAnnual] = useState<SeunResult>();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function calculate(event: FormEvent) {
    event.preventDefault();
    if (!date || !time) return;
    setLoading(true); setError(""); setAnnual(undefined);
    try {
      const response = await fetch(`${API_BASE}/v1/saju/calculate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ birth_local_datetime: kstIso(date, time) }) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.message ?? "계산 결과를 만들지 못했어요.");
      setResult(payload);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "계산 결과를 만들지 못했어요."); }
    finally { setLoading(false); }
  }

  async function calculateAnnual() {
    if (!date || !time) return;
    setLoading(true); setError("");
    try {
      const response = await fetch(`${API_BASE}/v1/seun/calculate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ birth_local_datetime: kstIso(date, time), target_local_datetime: `${year}-06-01T12:00:00+09:00` }) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.message ?? "세운 결과를 만들지 못했어요.");
      setAnnual(payload);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "세운 결과를 만들지 못했어요."); }
    finally { setLoading(false); }
  }

  return <main>
    <section className="hero"><p>DESTINY</p><h1>내 사주 살펴보기</h1><span>알고 있는 출생 정보만 입력해 주세요.</span></section>
    <section className="card">
      <form onSubmit={calculate}><label>생년월일<input type="date" value={date} onChange={(event) => setDate(event.target.value)} required /></label><label>태어난 시간<input type="time" value={time} onChange={(event) => setTime(event.target.value)} required /></label><p className="hint">기본 계산은 출생기록의 현지 시각과 절기 기준을 사용해요.</p><button disabled={loading}>{loading ? "계산하고 있어요…" : "사주 계산하기"}</button></form>
      {error && <p className="error">{error}</p>}
    </section>
    {result && <section className="card"><h2>계산 결과</h2><div className="pillars">{Object.entries(result.pillars).map(([position, pillar]) => <div key={position}><small>{{ year: "연주", month: "월주", day: "일주", hour: "시주" }[position]}</small><strong>{koreanPillar(pillar)}</strong></div>)}</div>{result.warnings.map((warning) => <p className="hint" key={warning}>{warning}</p>)}</section>}
    {result && <section className="card"><h2>세운 살펴보기</h2><p className="hint">어느 해를 살펴볼까요?</p><div className="year-row"><input aria-label="대상 연도" type="number" min="1900" max="2100" value={year} onChange={(event) => setYear(event.target.value)} /><button type="button" onClick={calculateAnnual} disabled={loading}>확인하기</button></div>{annual && <><h3>{annual.calendar_year}년의 간지 <b>{koreanPillar(annual.pillar)}</b></h3>{annualRelations(annual.relations).length ? <ul>{annualRelations(annual.relations).map((relation) => <li key={relation.relation_id}>{relation.participants.map((location) => locationLabels[location]).join("과 ")}: {relationLabels[relation.relation_type]}{relation.resulting_element ? ` · ${elementLabels[relation.resulting_element]}` : ""}</li>)}</ul> : <p>현재 지원되는 구조 관계는 확인되지 않았어요.</p>}<p className="disclosure">세운은 해당 해의 간지와 원국 사이에서 확인된 구조를 보여 줍니다. 좋고 나쁨을 단정하는 결과는 아니에요.</p></>}</section>}
  </main>;
}
