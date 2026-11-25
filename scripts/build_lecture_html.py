#!/usr/bin/env python3
"""lecture/*.md 를 하나의 강의안 HTML(lecture/강의안.html)로 묶는다.

사용법:
    pip install markdown
    python3 scripts/build_lecture_html.py
"""
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
LECTURE = ROOT / "lecture"
OUT = LECTURE / "강의안.html"
REPO_URL = "https://github.com/hglee04261-lab/-/blob/claude/magical-carson-565iar/"

SECTIONS = [
    ("00-강의안-2시간.md", "s0", "진행안", "전체 흐름"),
    ("01-AI-3대장-비교.md", "s1", "Part 1", "AI 3대장 비교"),
    ("02-SERMON-6단계-방법론.md", "s2", "Part 2", "S.E.R.M.O.N. 6단계"),
    ("03-3대장-실전-역할분담.md", "s3", "Part 3", "3대장 역할분담"),
    ("04-오케스트레이션.md", "s4", "Part 4", "오케스트레이션"),
    ("05-슬라이드-구성안.md", "a1", "부록 A", "슬라이드 구성안"),
    ("06-실습지.md", "a2", "부록 B", "수강생 실습지"),
]
ANCHOR = {name: sid for name, sid, *_ in SECTIONS}

TIMELINE = [
    ("여는 말", 10, "open"), ("Part 1 비교", 20, "p1"), ("Part 2 6단계", 30, "p2"),
    ("휴식", 10, "rest"), ("Part 3 실전", 25, "p3"), ("Part 4 지휘", 15, "p4"),
    ("마무리", 10, "open"),
]


def fix_links(md_text: str) -> str:
    def repl(m):
        label, target = m.group(1), m.group(2)
        if target.startswith(("http://", "https://", "#")):
            return m.group(0)
        name = Path(target.split("#")[0]).name
        if name in ANCHOR:
            return f"[{label}](#{ANCHOR[name]})"
        path = (LECTURE / target).resolve()
        try:
            rel = path.relative_to(ROOT).as_posix()
        except ValueError:
            return label
        return f"[{label}]({REPO_URL}{rel})"
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, md_text)


def render(md_text: str) -> str:
    md_text = fix_links(md_text)
    out = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists", "nl2br"])
    # 첫 h1 은 섹션 헤더로 대체하므로 제거
    out = re.sub(r"^<h1>.*?</h1>\s*", "", out, count=1, flags=re.S)
    out = out.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    out = out.replace("<pre>", '<pre><button class="copy" type="button">복사</button>')
    return out


def first_h1(md_text: str) -> str:
    m = re.search(r"^#\s+(.+)$", md_text, flags=re.M)
    return m.group(1).strip() if m else ""


def build() -> None:
    toc, body = [], []
    for fname, sid, kicker, short in SECTIONS:
        text = (LECTURE / fname).read_text(encoding="utf-8")
        title = re.sub(r"^Part \d+\.\s*", "", first_h1(text))
        cls = "appendix" if sid.startswith("a") else "part"
        toc.append(f'<li><a href="#{sid}"><span>{html.escape(kicker)}</span>{html.escape(short)}</a></li>')
        body.append(
            f'<section id="{sid}" class="{cls}">'
            f'<header class="sec-head"><p class="kicker">{html.escape(kicker)}</p>'
            f'<h1>{html.escape(title)}</h1></header>'
            f'<div class="prose">{render(text)}</div></section>'
        )

    total = sum(m for _, m, _ in TIMELINE)
    t, bars = 0, []
    for label, mins, kind in TIMELINE:
        start = f"{t // 60}:{t % 60:02d}"
        bars.append(
            f'<div class="seg seg-{kind}" style="flex:{mins}" title="{start} · {mins}분">'
            f'<b>{html.escape(label)}</b><small>{start} · {mins}분</small></div>'
        )
        t += mins

    page = TEMPLATE.format(toc="\n".join(toc), body="\n".join(body),
                           timeline="\n".join(bars), total=total)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI 설교 강의안</title>
<meta name="description" content="서울신학대학교 설교대학원 2시간 특강 — Gemini·ChatGPT·Claude로 준비하는 설교">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #faf8f4; --surface: #ffffff; --ink: #1f2430; --muted: #5d6472; --line: #e4dfd5;
  --accent: #23305a; --accent-soft: #e9ecf6; --code-bg: #f3f0ea;
  --gemini: #2f6fd6; --gpt: #1f9a6b; --claude: #d2702a; --rest: #b9b2a5;
  --p1: #2f6fd6; --p2: #23305a; --p3: #1f9a6b; --p4: #d2702a; --open: #7a6f5d;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #15171c; --surface: #1d2027; --ink: #e8e6e1; --muted: #a3a8b3; --line: #30343d;
    --accent: #aab8ec; --accent-soft: #252b3d; --code-bg: #23262e;
    --gemini: #6d9ef0; --gpt: #4cc79a; --claude: #f0a064; --rest: #5d5850;
    --p1: #4f86e3; --p2: #5b6bab; --p3: #2fae7f; --p4: #e08544; --open: #8c826f;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #15171c; --surface: #1d2027; --ink: #e8e6e1; --muted: #a3a8b3; --line: #30343d;
  --accent: #aab8ec; --accent-soft: #252b3d; --code-bg: #23262e;
  --gemini: #6d9ef0; --gpt: #4cc79a; --claude: #f0a064; --rest: #5d5850;
  --p1: #4f86e3; --p2: #5b6bab; --p3: #2fae7f; --p4: #e08544; --open: #8c826f;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{ margin: 0; background: var(--bg); color: var(--ink);
  font: 16px/1.75 "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
  word-break: keep-all; overflow-wrap: anywhere; }}
a {{ color: var(--accent); }}
.layout {{ display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 40px;
  max-width: 1200px; margin: 0 auto; padding: 0 24px; }}
nav.toc {{ position: sticky; top: 0; align-self: start; height: 100vh; overflow-y: auto; padding: 32px 0; }}
nav.toc h2 {{ font-size: 13px; letter-spacing: .08em; color: var(--muted); margin: 0 0 12px; }}
nav.toc ol {{ list-style: none; margin: 0; padding: 0; }}
nav.toc a {{ display: block; padding: 8px 12px; border-left: 3px solid transparent;
  color: var(--ink); text-decoration: none; font-size: 15px; border-radius: 0 6px 6px 0; }}
nav.toc a span {{ display: block; font-size: 12px; color: var(--muted); }}
nav.toc a:hover, nav.toc a.active {{ background: var(--accent-soft); border-left-color: var(--accent); }}
.theme-btn {{ margin-top: 20px; font: inherit; font-size: 13px; padding: 6px 12px; border-radius: 6px;
  border: 1px solid var(--line); background: var(--surface); color: var(--ink); cursor: pointer; }}
main {{ padding: 32px 0 80px; min-width: 0; }}
.hero {{ background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 36px 36px 28px; }}
.hero .kicker {{ margin: 0; color: var(--muted); font-size: 14px; }}
.hero h1 {{ font-family: "Noto Serif KR", serif; font-size: clamp(28px, 4.5vw, 40px); line-height: 1.3; margin: 8px 0 12px; }}
.hero .quote {{ font-family: "Noto Serif KR", serif; font-size: 18px; color: var(--accent); margin: 0 0 20px; }}
.meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 24px; padding: 0; list-style: none; }}
.meta li {{ background: var(--accent-soft); padding: 4px 12px; border-radius: 999px; font-size: 14px; }}
.ais {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }}
.ai {{ border: 1px solid var(--line); border-top: 4px solid; border-radius: 10px; padding: 12px 14px; }}
.ai b {{ display: block; }} .ai small {{ color: var(--muted); }}
.ai.g {{ border-top-color: var(--gemini); }} .ai.c {{ border-top-color: var(--gpt); }} .ai.cl {{ border-top-color: var(--claude); }}
.timeline {{ display: flex; gap: 3px; border-radius: 10px; overflow: hidden; }}
.seg {{ color: #fff; padding: 10px 8px; min-width: 0; }}
.seg b {{ display: block; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.seg small {{ font-size: 11px; opacity: .9; white-space: nowrap; }}
.seg-open {{ background: var(--open); }} .seg-p1 {{ background: var(--p1); }} .seg-p2 {{ background: var(--p2); }}
.seg-p3 {{ background: var(--p3); }} .seg-p4 {{ background: var(--p4); }} .seg-rest {{ background: var(--rest); }}
.tl-caption {{ font-size: 13px; color: var(--muted); margin: 8px 0 0; }}
section {{ margin-top: 56px; }}
.sec-head {{ border-bottom: 2px solid var(--ink); padding-bottom: 12px; margin-bottom: 24px; }}
.sec-head .kicker {{ margin: 0; font-weight: 700; color: var(--accent); letter-spacing: .04em; }}
.sec-head h1 {{ font-family: "Noto Serif KR", serif; font-size: clamp(22px, 3.2vw, 30px); line-height: 1.4; margin: 4px 0 0; }}
section.appendix .sec-head {{ border-bottom-style: dashed; }}
.prose h2 {{ font-size: 22px; margin: 40px 0 12px; padding-left: 12px; border-left: 5px solid var(--accent); line-height: 1.4; }}
.prose h3 {{ font-size: 18px; margin: 28px 0 8px; }}
.prose hr {{ border: 0; border-top: 1px solid var(--line); margin: 32px 0; }}
.prose blockquote {{ margin: 16px 0; padding: 12px 18px; background: var(--accent-soft);
  border-left: 4px solid var(--accent); border-radius: 0 8px 8px 0; }}
.prose blockquote p {{ margin: 4px 0; }}
.tbl {{ overflow-x: auto; margin: 16px 0; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }}
table {{ border-collapse: collapse; width: 100%; font-size: 15px; }}
th, td {{ padding: 9px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
th {{ background: var(--accent-soft); font-weight: 700; white-space: nowrap; }}
tr:last-child td {{ border-bottom: 0; }}
pre {{ position: relative; background: var(--code-bg); border: 1px solid var(--line); border-radius: 10px;
  padding: 16px 16px 16px; overflow-x: auto; font-size: 14px; line-height: 1.65; }}
pre code {{ font-family: "Noto Sans KR", ui-monospace, monospace; white-space: pre-wrap; }}
code {{ background: var(--code-bg); padding: 1px 5px; border-radius: 4px; font-size: .92em; }}
pre code {{ background: none; padding: 0; }}
.copy {{ position: absolute; top: 8px; right: 8px; font: inherit; font-size: 12px; padding: 3px 10px;
  border-radius: 6px; border: 1px solid var(--line); background: var(--surface); color: var(--muted); cursor: pointer; }}
.copy.done {{ color: var(--gpt); }}
footer {{ margin-top: 64px; color: var(--muted); font-size: 13px; border-top: 1px solid var(--line); padding-top: 16px; }}
@media (max-width: 860px) {{
  .layout {{ grid-template-columns: 1fr; padding: 0 16px; gap: 0; }}
  nav.toc {{ position: static; height: auto; padding: 16px 0 0; }}
  nav.toc ol {{ display: flex; gap: 6px; overflow-x: auto; padding-bottom: 6px; }}
  nav.toc li {{ flex: 0 0 auto; }}
  nav.toc a {{ border-left: 0; border-bottom: 3px solid transparent; border-radius: 6px; padding: 6px 10px; }}
  nav.toc h2, .theme-btn {{ display: none; }}
  .hero {{ padding: 24px 18px; }}
  .ais {{ grid-template-columns: 1fr; }}
  .timeline {{ flex-direction: column; gap: 2px; }}
  .seg {{ flex: none !important; display: flex; justify-content: space-between; padding: 8px 12px; }}
  .seg b {{ font-size: 14px; }} .seg small {{ font-size: 12px; }}
}}
@media print {{
  :root {{ --bg: #fff; --surface: #fff; --ink: #000; --muted: #444; --line: #ccc; --accent: #23305a; --accent-soft: #eef0f7; --code-bg: #f5f5f5; }}
  nav.toc, .copy, .theme-btn {{ display: none !important; }}
  .layout {{ display: block; max-width: none; padding: 0; }}
  body {{ font-size: 11pt; }}
  section {{ break-before: page; margin-top: 0; }}
  pre, .tbl, blockquote {{ break-inside: avoid; }}
  .seg, th {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
}}
</style>
</head>
<body>
<div class="layout">
<nav class="toc" aria-label="목차">
  <h2>목차</h2>
  <ol>
    <li><a href="#top"><span>개요</span>한눈에 보기</a></li>
{toc}
  </ol>
  <button class="theme-btn" type="button" id="themeBtn">다크/라이트 전환</button>
</nav>
<main>
<div class="hero" id="top">
  <p class="kicker">서울신학대학교 설교대학원 특강</p>
  <h1>AI와 함께 준비하는 최고의 설교</h1>
  <p class="quote">“AI는 서재를 넓혀 주지만, 강단에 대신 서 주지는 않는다.”</p>
  <ul class="meta">
    <li>대상: 현장 사역 목사·전도사</li><li>{total}분</li><li>이론 20 · 시연 50 · 실습 30</li><li>시연 본문: 누가복음 15:11–32</li>
  </ul>
  <div class="ais">
    <div class="ai g"><b>📚 Gemini — 사서</b><small>찾는다: 자료·출처·배경·사실검증</small></div>
    <div class="ai c"><b>💡 ChatGPT — 동역자</b><small>떠올린다: 제목·예화·적용·리허설</small></div>
    <div class="ai cl"><b>✍️ Claude — 편집자</b><small>다듬는다: 주해·명제·원고·검토</small></div>
  </div>
  <div class="timeline" role="img" aria-label="120분 강의 시간 배분">
{timeline}
  </div>
  <p class="tl-caption">막대 길이 = 시간 비율. 각 파트 상세는 아래 목차에서.</p>
</div>
{body}
<footer>원본: 저장소 <code>lecture/</code> 폴더의 Markdown 문서 · <code>python3 scripts/build_lecture_html.py</code>로 다시 생성</footer>
</main>
</div>
<script>
document.querySelectorAll("pre .copy").forEach(function (btn) {{
  btn.addEventListener("click", function () {{
    var code = btn.parentElement.querySelector("code");
    var text = code ? code.innerText : "";
    var done = function () {{ btn.textContent = "복사됨"; btn.classList.add("done");
      setTimeout(function () {{ btn.textContent = "복사"; btn.classList.remove("done"); }}, 1500); }};
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(text).then(done, function () {{}});
    }}
  }});
}});
var root = document.documentElement;
try {{ var saved = localStorage.getItem("theme"); if (saved) root.dataset.theme = saved; }} catch (e) {{}}
document.getElementById("themeBtn").addEventListener("click", function () {{
  var dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  root.dataset.theme = dark ? "light" : "dark";
  try {{ localStorage.setItem("theme", root.dataset.theme); }} catch (e) {{}}
}});
var links = Array.prototype.slice.call(document.querySelectorAll("nav.toc a"));
if ("IntersectionObserver" in window) {{
  var io = new IntersectionObserver(function (entries) {{
    entries.forEach(function (en) {{
      if (en.isIntersecting) {{
        links.forEach(function (a) {{ a.classList.toggle("active", a.getAttribute("href") === "#" + en.target.id); }});
      }}
    }});
  }}, {{ rootMargin: "-30% 0px -60% 0px" }});
  document.querySelectorAll("section, .hero").forEach(function (s) {{ io.observe(s); }});
}}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
