"""
GitHub Actions에서 실행되는 Claude 구현 스크립트.
docs/daily/YYYY-MM-DD/instructions.md 를 읽고
Claude API를 호출해 구현 결과를 리포트로 저장합니다.
"""

import os
import sys
import glob
from datetime import datetime
import anthropic

def find_latest_instructions():
    """가장 최근 instructions.md 찾기"""
    files = sorted(glob.glob("docs/daily/**/instructions.md", recursive=True))
    if not files:
        print("instructions.md 파일을 찾을 수 없습니다.")
        sys.exit(1)
    return files[-1]

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_report(content, date_str):
    os.makedirs("docs/implementation", exist_ok=True)
    path = f"docs/implementation/{date_str}-report.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"리포트 저장: {path}")
    return path

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY 환경변수가 없습니다.")
        sys.exit(1)

    instructions_path = find_latest_instructions()
    print(f"지시서: {instructions_path}")
    instructions = read_file(instructions_path)

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = """당신은 Destiny 프로젝트의 Python 백엔드 개발자입니다.
지시서를 읽고 구현 계획과 변경 사항을 Markdown 리포트로 작성합니다.
실제 코드 변경이 필요한 경우 diff 형식으로 제시합니다.
사실과 추정을 구분하고, 완료 기준과 잔존 위험을 명시합니다."""

    user_prompt = f"""다음 지시서를 검토하고 구현 리포트를 작성해 주세요.

---
{instructions}
---

리포트 형식:
# 구현 리포트 {datetime.now().strftime('%Y-%m-%d')}

## 요약
## 구현 계획
## 변경 파일
## 테스트 계획
## 잔존 위험
## 다음 단계
"""

    print("Claude API 호출 중...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )

    report = message.content[0].text
    date_str = datetime.now().strftime("%Y-%m-%d")
    save_report(report, date_str)
    print("완료")

if __name__ == "__main__":
    main()
