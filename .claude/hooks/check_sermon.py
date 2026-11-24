#!/usr/bin/env python3
"""설교 원고·핸드오프 패킷 자동 점검.

두 가지 방식으로 동작한다.
1) Claude Code PostToolUse 훅: stdin으로 받은 JSON의 tool_input.file_path 를 검사한다.
   - sermons/**/06-원고.md : [검증필요] 잔존, 창작 예화 표시, AI 투 표현, 낭독 시간 → Claude에게 참고 정보로 전달
   - sermons/**/handoff/to-*.md : 개인정보 의심 패턴 → Claude에게 경고(exit 2)
2) 명령행: python3 check_sermon.py <파일> [--report]
"""
import json
import re
import sys
from pathlib import Path

CHARS_PER_MIN = 300  # 한국어 설교 낭독 속도(공백 제외 글자/분) 대략값

AI_PHRASES = [
    "할 수 있습니다", "결론적으로", "여정", "깊이 있게", "다양한 측면",
    "중요한 것은", "살펴보겠습니다", "~것입니다", "시사하는 바",
]

PII_PATTERNS = {
    "전화번호": re.compile(r"01[016789][-\s.]?\d{3,4}[-\s.]?\d{4}"),
    "주민등록번호": re.compile(r"\d{6}[-\s]?[1-4]\d{6}"),
    "이메일": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "실명+직분 호칭": re.compile(r"[가-힣]{2,4}\s?(집사|권사|장로|성도|청년)님?(의|이|가|은|는|께서)\s"),
    "민감 상담 키워드": re.compile(r"(이혼|암\s?투병|우울증|파산|외도|자살)"),
}


def check_manuscript(text: str) -> list[str]:
    notes = []
    unverified = len(re.findall(r"\[검증필요\]", text))
    if unverified:
        notes.append(f"[검증필요] 표시 {unverified}개 남음 — 최종본 전 모두 확인·삭제 필요")

    created = len(re.findall(r"\[창작\]", text))
    if created:
        notes.append(f"[창작] 예화 {created}개 — 설교 때 창작임이 드러나게 말할 것")

    quote_like = len(re.findall(r"(라고 말했|이 말했|의 말처럼|는 이렇게 말합니다)", text))
    citations = len(re.findall(r"\(출처:", text))
    if quote_like > citations:
        notes.append(f"인용 표현 {quote_like}곳 / 출처 표기 {citations}곳 — 출처 누락 의심")

    hits = {p: text.count(p.replace("~", "")) for p in AI_PHRASES}
    hits = {p: n for p, n in hits.items() if n >= 2}
    if hits:
        notes.append("AI 투 표현 반복: " + ", ".join(f"'{p}'×{n}" for p, n in hits.items()))

    body = re.sub(r"\s", "", re.sub(r"^#.*$", "", text, flags=re.M))
    minutes = len(body) / CHARS_PER_MIN
    notes.append(f"낭독 예상 약 {minutes:.0f}분 (공백 제외 {len(body):,}자 기준)")
    return notes


def check_pii(text: str) -> list[str]:
    found = []
    for name, pat in PII_PATTERNS.items():
        m = pat.findall(text)
        if m:
            found.append(f"{name} 의심 {len(m)}건")
    return found


def classify(path: Path) -> str | None:
    p = path.as_posix()
    if "/sermons/" not in "/" + p and not p.startswith("sermons/"):
        return None
    if path.name == "06-원고.md":
        return "manuscript"
    if path.parent.name == "handoff" and path.name.startswith("to-"):
        return "handoff"
    return None


def run_hook() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    fp = (data.get("tool_input") or {}).get("file_path")
    if not fp:
        return 0
    path = Path(fp)
    kind = classify(path)
    if not kind or not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")

    if kind == "handoff":
        pii = check_pii(text)
        if pii:
            print(
                f"⚠️ 핸드오프 패킷 개인정보 점검({path.name}): " + "; ".join(pii)
                + ". 외부 AI로 보내기 전에 익명화하고 설교자에게 알리세요.",
                file=sys.stderr,
            )
            return 2
        return 0

    notes = check_manuscript(text)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "원고 자동 점검: " + " | ".join(notes),
        }
    }, ensure_ascii=False))
    return 0


def run_cli(args: list[str]) -> int:
    path = Path(args[0])
    text = path.read_text(encoding="utf-8")
    print(f"# 자동 점검: {path}")
    for n in check_manuscript(text):
        print(f"- {n}")
    pii = check_pii(text)
    print(f"- 개인정보 의심: {'; '.join(pii) if pii else '없음'}")
    return 0


if __name__ == "__main__":
    argv = [a for a in sys.argv[1:] if a != "--report"]
    sys.exit(run_cli(argv) if argv else run_hook())
