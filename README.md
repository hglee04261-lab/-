# AI 설교 하네스 — Gemini · ChatGPT · Claude로 설교 준비하기

서울신학대학교 설교대학원 특강(2시간)용 **강의 자료 + 실습 하네스**입니다.
대상: 설교 현장에서 사역 중인 목사님·전도사님
원칙: **이론은 짧게, 방법은 바로 쓸 수 있게.**

> AI는 설교를 대신 쓰는 도구가 아니라, 설교자가 **더 깊이 듣고(본문), 더 넓게 찾고(자료), 더 정확히 말하도록(검증)** 돕는 조수입니다.

---

## 강의 흐름 (120분)

| 시간 | 파트 | 자료 |
|---|---|---|
| 0:00–0:10 | 여는 말: 설교자의 자리와 AI의 자리 | [lecture/00-강의안-2시간.md](lecture/00-강의안-2시간.md) |
| 0:10–0:30 | **Part 1. AI 3대장 비교** (설교 준비 관점의 장단점) | [lecture/01-AI-3대장-비교.md](lecture/01-AI-3대장-비교.md) |
| 0:30–1:00 | **Part 2. 최고의 설교를 위한 S.E.R.M.O.N. 6단계** | [lecture/02-SERMON-6단계-방법론.md](lecture/02-SERMON-6단계-방법론.md) |
| 1:00–1:10 | 휴식 | |
| 1:10–1:35 | **Part 3. 3대장 역할분담 실전 시연** | [lecture/03-3대장-실전-역할분담.md](lecture/03-3대장-실전-역할분담.md) |
| 1:35–1:50 | **Part 4. 오케스트레이션** (전 과정 지휘하기) | [lecture/04-오케스트레이션.md](lecture/04-오케스트레이션.md) |
| 1:50–2:00 | 윤리 가드레일 · Q&A · 과제 | [guidelines/윤리-신학-가드레일.md](guidelines/윤리-신학-가드레일.md) |

슬라이드 구성안: [lecture/05-슬라이드-구성안.md](lecture/05-슬라이드-구성안.md)
수강생 실습지(배포용): [lecture/06-실습지.md](lecture/06-실습지.md)
시연 예제(누가복음 15:11–32): [examples/눅15-시연.md](examples/눅15-시연.md)

---

## 폴더 구조

```
CLAUDE.md                  ← Claude Code가 따르는 하네스 운영 원칙(지휘자 규칙)
.claude/
  agents/                  ← 전문 서브에이전트 5명
    exegete.md               본문 주해가
    theology-reviewer.md     신학 검증관(웨슬리안·성결 전통)
    homiletics-coach.md      설교학 코치
    fact-checker.md          사실·인용 검증관
    congregation-voice.md    청중 대변인
  commands/                ← 슬래시 명령 (오케스트레이션 단계별)
    sermon-start.md          /sermon-start  새 설교 프로젝트 시작
    handoff.md               /handoff       Gemini·GPT로 보낼 패킷 생성
    integrate.md             /integrate     외부 AI 결과 통합
    crosscheck.md            /crosscheck    다중 에이전트 교차검증
    finalize.md              /finalize      최종 점검·원고 확정
  skills/sermon-orchestrator/SKILL.md  ← 전체 파이프라인 지휘 스킬
  hooks/check_sermon.py    ← 원고 저장 시 [검증필요] 표시·출처 누락 자동 경고
  settings.json
lecture/                   ← 강의안 (Part 0~4, 슬라이드, 실습지)
prompts/                   ← AI별 복사용 프롬프트 카드
templates/                 ← 설교 브리프 · 핸드오프 패킷 · AI 사용기록 · 원고 양식
rubrics/                   ← 최종 점검 체크리스트(환각·신학·설교학)
guidelines/                ← 윤리·신학 가드레일, 강의 전 최신정보 점검표
examples/                  ← 강의 시연용 완성 예제
sermons/                   ← 실제 설교 작업 공간 (설교 1편 = 폴더 1개)
```

---

## 세 가지 사용 수준

| 수준 | 누구에게 | 방법 |
|---|---|---|
| **Level 1 — 수동 릴레이** | 모든 수강생 | 세 AI 앱을 열어 두고 `prompts/`의 카드를 복사해 단계별로 사용. 결과는 `templates/핸드오프-패킷.md` 양식으로 다음 AI에 넘김 |
| **Level 2 — 프로젝트 고정** | 매주 설교하는 분 | Claude Projects / ChatGPT Projects / Gemini Gem·Notebook에 `prompts/05-프로젝트-지침.md`를 넣어 "나만의 설교 조수" 3명 상주 |
| **Level 3 — Claude Code 지휘** | 디지털 숙련자 | 이 저장소를 Claude Code로 열고 `/sermon-start` → `/handoff` → `/integrate` → `/crosscheck` → `/finalize` |

### Level 3 빠른 시작

```bash
claude
```

Claude Code 안에서:

```
/sermon-start 누가복음 15:11-32 | 2026-12-06 주일 2부 | 장년 | 탕자의 비유, 기다리시는 아버지
```

---

## 강의 당일 체크

AI 서비스는 몇 달마다 모델명·요금·기능이 바뀝니다. 강의 전날 [guidelines/강의전-최신정보-점검.md](guidelines/강의전-최신정보-점검.md)로 확인하세요.
