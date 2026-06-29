#!/usr/bin/env python3
"""collect.py — 평가 대상 스킬을 한 번에 모아 채점 준비를 끝낸다.

대상 스킬의 SKILL.md 본문, 보조 파일(references·scripts) 목록, 흔한 감점 신호
휴리스틱, 그리고 빈 채점표를 한 번에 출력한다. 표준 라이브러리만 쓴다(의존성 0).

사용법:
    python3 collect.py <스킬-폴더-또는-SKILL.md-경로>
    python3 collect.py .            # 현재 폴더를 대상으로

휴리스틱은 어디까지나 '참고용 힌트'다. 최종 합격/미달은 rubric.md 의
합격선 문장으로 사람이 판정한다.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VAGUE_WORDS = ["잘", "적당히", "알아서", "적절히", "등등", "필요시", "대충"]
PERSONAL_PATHS = ["/Users/", r"C:\\", "바탕화면", "Desktop", "내 폴더", "/home/"]
METRIC_RE = re.compile(r"\d+\s*(분|초|시간|%|배|회)")
IO_HINTS = ["입력", "출력", "예시", "example", "input", "output"]

AXES = [
    ("① 명세 또렷함", "입력·처리·출력·합격기준이 각각 한 문장, 모호어 없음"),
    ("② 검증 루프", "입력→출력 한 세트 + '이래서 이렇게 고쳤다' 한 줄"),
    ("③ 진짜 업무성", "'매주 월요일, 자막→블로그'처럼 구체적인 반복 업무"),
    ("④ 동료 이식성", "'○○할 때 쓰세요' 꼴, 개인 경로·사정이 안 박힘"),
    ("⑤ 임팩트", "'회당 30분→5분'처럼 수치로 말할 수 있음"),
]


def find_skill_md(target: Path) -> Path | None:
    """경로가 폴더면 그 안의 SKILL.md를, 파일이면 그 파일을 돌려준다."""
    if target.is_file():
        return target
    if target.is_dir():
        for name in ("SKILL.md", "skill.md"):
            cand = target / name
            if cand.exists():
                return cand
    return None


def heuristics(body: str) -> list[str]:
    """본문에서 흔한 감점 신호를 찾아 사람이 볼 힌트로 돌려준다."""
    hints: list[str] = []

    found_vague = sorted({w for w in VAGUE_WORDS if w in body})
    if found_vague:
        hints.append(f"① 모호어 발견: {', '.join(found_vague)} → 명세 또렷함 감점 신호")

    if not any(h in body.lower() for h in IO_HINTS):
        hints.append("② 입력/출력 예시로 보이는 단어가 없음 → 검증 루프 감점 신호")

    found_paths = sorted({p for p in PERSONAL_PATHS if p in body})
    if found_paths:
        hints.append(f"④ 개인 경로/사정 박힘: {', '.join(found_paths)} → 동료 이식성 감점 신호")

    if not METRIC_RE.search(body):
        hints.append("⑤ 줄어든 시간·횟수 수치(분·회당·%·배)가 없음 → 임팩트 감점 신호")

    if not hints:
        hints.append("뚜렷한 감점 신호 없음 — 합격선 문장으로 직접 판정할 것.")
    return hints


def supporting_files(skill_dir: Path, skill_md: Path) -> list[str]:
    """references·scripts 등 보조 파일을 상대경로로 모은다."""
    out: list[str] = []
    for p in sorted(skill_dir.rglob("*")):
        if p.is_file() and p.resolve() != skill_md.resolve():
            out.append(str(p.relative_to(skill_dir)))
    return out


def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").expanduser()
    if not target.exists():
        print(f"[오류] 경로를 찾을 수 없습니다: {target}", file=sys.stderr)
        return 1

    skill_md = find_skill_md(target)
    if skill_md is None:
        print(f"[오류] SKILL.md 를 찾을 수 없습니다: {target}", file=sys.stderr)
        return 1

    skill_dir = skill_md.parent
    body = skill_md.read_text(encoding="utf-8", errors="replace")

    name_match = re.search(r"^name:\s*(.+)$", body, re.MULTILINE)
    skill_name = name_match.group(1).strip() if name_match else skill_dir.name

    print("=" * 60)
    print(f"평가 대상: {skill_name}")
    print(f"SKILL.md : {skill_md}")
    print("=" * 60)

    print("\n## SKILL.md 본문\n")
    print(body.rstrip())

    files = supporting_files(skill_dir, skill_md)
    print("\n## 보조 파일")
    if files:
        for f in files:
            print(f"  - {f}")
    else:
        print("  (없음)")

    print("\n## 휴리스틱 힌트 (참고용)")
    for h in heuristics(body):
        print(f"  - {h}")

    print("\n## 채점표 (rubric.md 합격선으로 채울 것)\n")
    print(f"## 검수 결과 — {skill_name}   합계 _/10\n")
    print("| 축 | 판정 | 근거 (본문 한 줄) |")
    print("|---|---|---|")
    for axis, _crit in AXES:
        print(f"| {axis} | 합격/부분/미달 | \"…\" |")
    print("\n🎯 오늘 고칠 자리: <가장 짧은 축>")
    print("🩺 걸린 결함: <뭉뚱그린 명세 / 한 방에 끝 / toy 예제 중>")
    print("💊 한 줄 처방: <복붙용 프롬프트 한 줄>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
