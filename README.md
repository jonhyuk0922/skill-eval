# skill-eval — 내 스킬, 다섯 축으로 검수

내가 만든 [Claude Code](https://claude.com/claude-code) 스킬을 **다섯 축 기준**으로 점검해
축마다 합격/부분/미달을 매기고, **가장 짧은 축 한 가지**와 그 축을 올리는 **한 줄 처방**을 돌려주는 스킬입니다.

> 점수를 매기는 게 목적이 아닙니다. "다음에 뭘 한 가지 고칠지"를 집어주는 게 목적입니다.

## 다섯 축

| 축 | 여기까지면 합격 |
|---|---|
| ① 명세 또렷함 | 입력·처리·출력·합격기준이 각각 한 문장, 모호어 없음 |
| ② 검증 루프 | 입력→출력 한 세트 + "이래서 이렇게 고쳤다" 한 줄 |
| ③ 진짜 업무성 | "매주 월요일, 자막→블로그"처럼 구체적인 반복 업무 |
| ④ 동료 이식성 | "○○할 때 쓰세요" 꼴, 개인 폴더 경로·내 사정이 안 박힘 |
| ⑤ 임팩트 | "회당 30분→5분"처럼 수치로 말할 수 있음 |

다섯 줄 중 가장 짧은 한 축이, 오늘 고칠 자리입니다.

## 설치

### 1) `skills` CLI (권장 · npm 처럼 한 줄)

```bash
npx skills add jonhyuk0922/skill-eval
```

[`skills`](https://github.com/vercel-labs/skills) CLI가 이 레포를 `.claude/skills/skill-eval/` 에 설치합니다.
별도 전역 설치 없이 `npx` 한 줄이면 끝납니다.

### 2) 수동 설치 (git clone)

```bash
# 프로젝트 한정으로 쓰려면
git clone https://github.com/jonhyuk0922/skill-eval .claude/skills/skill-eval

# 모든 프로젝트에서 쓰려면 (전역)
git clone https://github.com/jonhyuk0922/skill-eval ~/.claude/skills/skill-eval
```

설치 후 Claude Code를 다시 시작하면 스킬이 잡힙니다.

## 사용법

설치하면 자연어로 부릅니다. 키워드: `내 스킬 검수`, `스킬 평가해줘`, `다섯 축으로 봐줘`, `skill review`.

```
내가 만든 ~/.claude/skills/news-digest 스킬 다섯 축으로 검수해줘
```

대상 경로(스킬 폴더 또는 `SKILL.md`)를 함께 주면 바로 채점합니다.

### 스크립트만 따로 (의존성 0)

채점 준비(본문 + 보조 파일 + 감점 힌트 + 빈 채점표)를 터미널에서 바로 보고 싶다면:

```bash
python3 scripts/collect.py <스킬-폴더-또는-SKILL.md-경로>
```

## 출력 예시

```
## 검수 결과 — news-digest   합계 6/10

| 축 | 판정 | 근거 (본문 한 줄) |
|---|---|---|
| ① 명세 또렷함 | 합격 | "입력: RSS URL 목록 / 출력: 마크다운 요약 3줄" |
| ② 검증 루프   | 미달 | (돌려보고 고친 흔적 없음) |
| ③ 진짜 업무성 | 합격 | "매주 월요일 아침 뉴스레터 초안" |
| ④ 동료 이식성 | 부분 | "/Users/jo/Desktop 경로가 박혀 있음" |
| ⑤ 임팩트     | 미달 | (줄어든 시간 수치 없음) |

🎯 오늘 고칠 자리: ② 검증 루프
🩺 걸린 결함: 한 방에 끝
💊 한 줄 처방: 지난주 실제 RSS 하나로 돌려보고, 빗나간 요약 한 건을 고친 뒤
   "이래서 이렇게 고쳤다"를 SKILL.md에 한 줄 남겨줘.
```

## 무엇이 들어 있나

```
skill-eval/
├── SKILL.md                       # 스킬 본체 (검수 절차)
├── references/
│   ├── rubric.md                  # 다섯 축 기준표 + 채점 척도 + 3대 결함·처방
│   └── scorecard-template.md      # 채점표 출력 형식
└── scripts/
    └── collect.py                 # 대상 스킬 수집 + 감점 힌트 + 빈 채점표 (stdlib only)
```

## 라이선스

[MIT](./LICENSE) © 2026 이종혁 (조녁컴퍼니)
