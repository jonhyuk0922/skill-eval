#!/usr/bin/env python3
"""collect.py — 평가 대상 스킬을 한 번에 모아 채점 준비를 끝낸다.

대상 스킬의 SKILL.md 본문, 보조 파일(references·scripts) 목록, 감점 신호,
그리고 빈 채점표를 한 번에 출력한다. 표준 라이브러리만 쓴다(의존성 0).

사용법:
    python3 collect.py <스킬-폴더-또는-SKILL.md-경로>
    python3 collect.py .            # 현재 폴더를 대상으로

축을 둘로 나눈다:
  · ①명세·④이식성·⑤임팩트 — 모호어·개인경로·수치처럼 글자로 잡히므로 '자동 신호'를 준다.
  · ②검증 루프·③진짜 업무성 — 단어가 우연히 있거나 없을 수 있어 기계가 못 가린다.
    그래서 이 둘은 자동 판정하지 않고, 사람이 채울 '확인란'만 내놓는다.
빈 채점표는 references/scorecard-template.md 를 단일 출처로 읽어 찍는다.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ── ① 명세 또렷함: 모호어 (자동) ─────────────────────────────────────
VAGUE_WORDS = ["적당히", "알아서", "적절히", "대충", "알맞게", "좋게", "등등", "필요시"]
# '잘'은 한 글자라 잘못·잘하다·칼잘 처럼 멀쩡한 단어에 박힌다 →
# 앞뒤가 한글이 아닌 '독립 토큰 잘'만 모호어로 본다.
JAL_RE = re.compile(r"(?<![가-힣])잘(?![가-힣])")

# ── ④ 동료 이식성: 하드코딩된 개인 경로 (자동) ───────────────────────
UNIX_HOME_RE = re.compile(r"/Users/|/home/")   # 개인 홈 경로
WIN_PATH_RE = re.compile(r"[A-Za-z]:\\")        # C:\ 형태 (백슬래시 1개)
KO_DESKTOP = "바탕화면"

# ── ⑤ 임팩트: 줄어든 시간·횟수 수치 (자동, 한글 수사 일부 포함) ───────
METRIC_RE = re.compile(r"\d+\s*(분|초|시간|%|배|회|건)|절반|두\s*배|세\s*배|반으로")

# ── ②③ 참고용 원시 관찰 (판정이 아니라 '참고 숫자'로만 쓴다) ─────────
EXAMPLE_MARKERS = ["→", "->", "예시", "example", "e.g", "```", "입력:", "출력:", "input:", "output:"]
LOOP_WORDS = ["고쳤", "고친", "테스트", "검증", "돌려", "재시도", "이래서"]
REPEAT_WORDS = ["매주", "매일", "매월", "매번", "요일", "반복", "할 때마다", "할때마다", "주간", "정기", "트리거"]

AXES = [
    ("① 명세 또렷함", "입력·처리·출력·합격기준이 각각 한 문장, 모호어 없음"),
    ("② 검증 루프", "입력→출력 한 세트 + '이래서 이렇게 고쳤다' 한 줄"),
    ("③ 진짜 업무성", "'매주 월요일, 자막→블로그'처럼 구체적인 반복 업무"),
    ("④ 동료 이식성", "'○○할 때 쓰세요' 꼴, 개인 경로·사정이 안 박힘"),
    ("⑤ 임팩트", "'회당 30분→5분'처럼 수치로 말할 수 있음"),
]

TEMPLATE_REL = Path("references") / "scorecard-template.md"


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


def auto_signals(body: str) -> list[str]:
    """기계가 비교적 잘 잡는 ①④⑤ 축만 자동 신호로 돌려준다.

    ②③은 여기서 판정하지 않는다 — 사람 확인란(human_checks)으로 넘긴다.
    """
    hints: list[str] = []

    # ① 모호어
    vague = sorted({w for w in VAGUE_WORDS if w in body})
    if JAL_RE.search(body):
        vague.append("잘")
    if vague:
        hints.append("① 모호어: " + ", ".join(vague) + " → 명세 또렷함 감점 신호")

    # ④ 개인 경로 (중복 없이 한 줄로)
    paths = []
    if UNIX_HOME_RE.search(body):
        paths.append("/Users/ · /home/")
    if WIN_PATH_RE.search(body):
        paths.append(r"C:\ 드라이브 경로")
    if KO_DESKTOP in body:
        paths.append("바탕화면")
    if paths:
        hints.append("④ 개인 경로 박힘: " + ", ".join(paths) + " → 동료 이식성 감점 신호")

    # ⑤ 임팩트 수치
    if not METRIC_RE.search(body):
        hints.append("⑤ 줄어든 시간·횟수 수치(분·회당·%·배·절반)가 없음 → 임팩트 감점 신호")

    if not hints:
        hints.append("①④⑤ 축엔 뚜렷한 감점 신호 없음 — 합격선 문장으로 직접 판정할 것.")
    return hints


def human_checks(body: str) -> list[str]:
    """②③은 기계가 못 가린다 — 판정 대신 '사람이 채울 확인란'을 낸다.

    원시 관찰(마커 개수)은 참고 숫자로만 덧붙인다. 이 숫자가 곧 합격/미달이 아니다.
    """
    ex = sum(1 for m in EXAMPLE_MARKERS if m in body.lower())
    lp = sum(1 for w in LOOP_WORDS if w in body)
    rp = sum(1 for w in REPEAT_WORDS if w in body)
    return [
        "② 검증 루프  [ 사람 판정 ]",
        "   [ ] 본문에 '실제 입력→출력 한 세트'가 있나?",
        "   [ ] '이래서 이렇게 고쳤다'(돌려보고 고친) 흔적이 있나?",
        f"   (참고 숫자: 예시 마커 {ex} · 고침/검증어 {lp} — 판정 근거 아님, 본문 읽고 사람이 정한다)",
        "③ 진짜 업무성  [ 사람 판정 ]",
        "   [ ] 이게 정말 네가 반복하는 실제 업무인가? (요일·트리거·산출물로 말할 수 있나?)",
        f"   (참고 숫자: 반복·트리거어 {rp} — 단어 유무로 판정하지 말 것)",
    ]


# 보조 파일 목록에서 뺄 잡음 (.git 내부, 캐시, OS 부산물 등)
IGNORE_DIRS = {".git", "__pycache__", ".mypy_cache", ".pytest_cache", "node_modules", ".venv"}
IGNORE_SUFFIXES = {".pyc", ".pyo"}
IGNORE_NAMES = {".DS_Store"}


def supporting_files(skill_dir: Path, skill_md: Path) -> list[str]:
    """references·scripts 등 '진짜' 보조 파일만 상대경로로 모은다.

    .git 내부·캐시·OS 부산물은 스킬 내용이 아니므로 건너뛴다
    (대상 스킬이 git 레포여도 목록이 깨끗하게 나오도록).
    """
    out: list[str] = []
    for p in sorted(skill_dir.rglob("*")):
        if not p.is_file() or p.resolve() == skill_md.resolve():
            continue
        rel = p.relative_to(skill_dir)
        if set(rel.parts) & IGNORE_DIRS:
            continue
        if p.suffix in IGNORE_SUFFIXES or p.name in IGNORE_NAMES:
            continue
        out.append(str(rel))
    return out


def _first_fenced_block(text: str) -> str | None:
    """마크다운에서 첫 ``` … ``` 블록 안쪽을 돌려준다(펜스 줄 제외)."""
    m = re.search(r"```[^\n]*\n(.*?)\n```", text, re.DOTALL)
    return m.group(1) if m else None


def render_blank_scorecard(skill_name: str) -> str:
    """채점표를 references/scorecard-template.md(단일 출처)에서 읽어 찍는다.

    템플릿을 못 찾으면 AXES 로 최소 형태를 만들어 폴백한다(스크립트만 떼어가도 동작).
    """
    template_path = Path(__file__).resolve().parent.parent / TEMPLATE_REL
    try:
        block = _first_fenced_block(template_path.read_text(encoding="utf-8"))
    except OSError:
        block = None
    if block:
        return block.replace("<스킬 이름>", skill_name).replace("<N>", "_")

    # 폴백: 템플릿 파일이 없을 때만 쓰는 최소 형태
    lines = [
        f"## 검수 결과 — {skill_name}   합계 _/10",
        "",
        "| 축 | 판정 | 근거 (본문 한 줄) |",
        "|---|---|---|",
    ]
    for axis, _crit in AXES:
        mark = " 〔사람〕" if axis.startswith(("②", "③")) else ""
        lines.append(f"| {axis}{mark} | <합격/부분/미달> | \"…\" |")
    lines += [
        "",
        "🎯 오늘 고칠 자리: <가장 짧은 축>",
        "🩺 걸린 결함: <뭉뚱그린 명세 / 한 방에 끝 / toy 예제 중>",
        "💊 한 줄 처방: <복붙용 프롬프트 한 줄>",
    ]
    return "\n".join(lines)


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

    print("\n## 자동 신호 (①④⑤ — 기계가 비교적 잘 잡는 축)")
    for h in auto_signals(body):
        print(f"  - {h}")

    print("\n## 사람이 직접 표시 (②③ — 기계가 못 가리는 축)")
    print("  아래 [ ] 를 본문 읽고 사람이 채운다. 참고 숫자는 근거가 아니다.")
    for line in human_checks(body):
        print(f"  {line}")

    print("\n## 채점표 (rubric.md 합격선으로 채울 것)\n")
    print(render_blank_scorecard(skill_name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
