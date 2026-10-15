#!/usr/bin/env python3
"""สร้างคู่มือ KitchenAI (ฉบับนักศึกษา เรียนรู้ด้วยตนเอง) เป็น HTML → PDF จากซอร์สโค้ดจริงใน git

python3 docs/build_guide.py
ต้องมี: pygments, pypdf, reportlab, Google Chrome, ฟอนต์ TH Sarabun New
โค้ดที่แสดงดึงจาก tag `starter` และ `done` ด้วย git show (คู่มือจึงตรงกับโค้ดเสมอ)
"""
import html
import re
import subprocess
from datetime import date
from io import BytesIO
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import BashLexer, DartLexer, DiffLexer, JsonLexer, YamlLexer, TextLexer

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPO = "https://github.com/kittipongnuanyai/KitchenAI"
START_TAG = "starter"
DONE_TAG = "done"
OUT_HTML = DOCS / "KitchenAI-คู่มือ.html"
OUT_PDF_RAW = DOCS / "_raw.pdf"
OUT_PDF = DOCS / "KitchenAI-คู่มือ.pdf"

FMT = HtmlFormatter(style="friendly", nowrap=True)
THAI_MONTHS = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
today = date.today()
TODAY_TH = f"{today.day} {THAI_MONTHS[today.month - 1]} {today.year + 543}"
LEXERS = {"dart": DartLexer, "bash": BashLexer, "json": JsonLexer, "diff": DiffLexer, "yaml": YamlLexer, "text": TextLexer}


# ---------------------------------------------------------------- helpers
def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


def src_at(tag: str, rel: str) -> str:
    out = git("show", f"{tag}:{rel}")
    if not out:
        raise SystemExit(f"ไม่พบ {rel} ใน tag {tag}")
    return out


def between(text: str, start: str, end: str | None = None, include_end: bool = False) -> str:
    """ตัดช่วงโค้ดจากบรรทัดที่มี start ถึง (ก่อน) บรรทัดที่มี end — รองรับ marker หลายบรรทัด"""
    i = text.find(start)
    if i < 0:
        raise SystemExit(f"ไม่พบ marker เริ่ม: {start[:50]!r}")
    i = text.rfind("\n", 0, i) + 1  # ถอยไปต้นบรรทัด
    if end is None:
        return text[i:]
    j = text.find(end, i + len(start))
    if j < 0:
        raise SystemExit(f"ไม่พบ marker จบ: {end[:50]!r} (หลัง {start[:30]!r})")
    if include_end:
        j = text.find("\n", j + len(end))
        return text[i:j if j >= 0 else len(text)]
    j = text.rfind("\n", 0, j) + 1
    return text[i:j].rstrip("\n")


def dedent_block(text: str) -> str:
    import textwrap
    return textwrap.dedent(text)


def code(text: str, lang: str = "dart", path: str | None = None, note: str | None = None) -> str:
    body = highlight(text.rstrip("\n"), LEXERS[lang](), FMT)
    n = text.rstrip("\n").count("\n") + 1
    right = note if note else f"{n} บรรทัด"
    cap = f'<div class="codecap"><span class="path">{html.escape(path)}</span><span class="lines">{right}</span></div>' if path else ""
    return f'<div class="codeblock">{cap}<pre class="hl">{body}</pre></div>'


def file_block(rel: str, tag: str = DONE_TAG, lang: str = "dart", note: str = "ไฟล์เต็ม") -> str:
    return code(src_at(tag, rel), lang, rel, note=note)


def part_block(rel: str, start: str, end: str | None = None, tag: str = DONE_TAG, note: str = "บางส่วน", include_end: bool = False) -> str:
    return code(dedent_block(between(src_at(tag, rel), start, end, include_end)), "dart", rel, note=note)


def diff_block(rel: str) -> str:
    out = git("diff", "-U2", "--no-color", START_TAG, DONE_TAG, "--", rel)
    lines = out.splitlines()
    body = "\n".join(l for l in lines if not (l.startswith("diff --git") or l.startswith("index ")
                                              or l.startswith("--- ") or l.startswith("+++ ")))
    added = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
    return code(body, "diff", rel, note=f"starter → done · +{added} / −{removed} บรรทัด")


def box(kind: str, title: str, body: str) -> str:
    return f'<div class="box {kind}"><div class="boxtitle">{title}</div>{body}</div>'


def ul(*items: str) -> str:
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def ol(*items: str) -> str:
    return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def p(t: str) -> str:
    return f"<p>{t}</p>"


def h3(t: str) -> str:
    return f"<h3>{t}</h3>"


def c(t: str) -> str:
    return f"<code>{html.escape(t)}</code>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    h = "".join(f"<th>{x}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f'<table class="tbl"><tr>{h}</tr>{b}</table>'


def fig(*names_caps: tuple[str, str], width_mm: int = 52) -> str:
    items = []
    for name, cap in names_caps:
        f = DOCS / "shots" / f"{name}.png"
        if not f.exists():
            items.append(f'<figure class="shot" style="width:{width_mm}mm"><div class="noshot">(ไม่มีภาพ {name})</div><figcaption>{cap}</figcaption></figure>')
        else:
            items.append(f'<figure class="shot" style="width:{width_mm}mm"><img src="shots/{name}.png"><figcaption>{cap}</figcaption></figure>')
    return '<div class="figrow">' + "".join(items) + "</div>"


STEPS: list[dict] = []


def step(no: int, title: str, minutes: int, goal: str, body: str, kind: str = "อ่าน+ทำตาม") -> None:
    STEPS.append(dict(no=no, title=title, minutes=minutes, goal=goal, body=body, kind=kind))


AS = "Android Studio"
DONE = src_at(DONE_TAG, "lib/data/gemini_client.dart")

# ================================================================ STEP 1
step(1, "ขอ Gemini API key (ฟรี) และทดลองยิงคำขอแรก", 25,
     "มี API key ของตัวเอง และเห็นคำตอบจาก Gemini บนหน้าจอด้วย curl ก่อนเขียนแอป",
     p("ก่อนจะให้แอป \"คุยกับ AI\" ได้ เราต้องมี <b>API key</b> ซึ่งเป็นรหัสผ่านยาว ๆ ที่บอก Google ว่าคำขอนี้มาจากบัญชีของเรา Google ให้ใช้ Gemini ฟรีในปริมาณจำกัดต่อวัน (เพียงพอสำหรับทำแล็บนี้ทั้งเทอม) ไม่ต้องใส่บัตรเครดิต")
     + h3("1.1 สร้าง key ใน Google AI Studio")
     + ol("เปิดเบราว์เซอร์ไปที่ <b>https://aistudio.google.com/apikey</b> แล้ว sign in ด้วยบัญชี Google (ใช้ Gmail ส่วนตัวได้ บัญชีมหาวิทยาลัยบางแห่งอาจถูกแอดมินปิดไว้ ถ้ากดสร้างไม่ได้ให้สลับบัญชี)",
          "ครั้งแรกจะมีหน้าให้ยอมรับข้อตกลง (Terms of Service) กดยอมรับ",
          "กดปุ่ม <b>Create API key</b> → ถ้าถามให้เลือกโปรเจกต์ ให้เลือก <i>Create API key in new project</i> หรือโปรเจกต์ที่ระบบสร้างให้ (ชื่อ Gemini API / Default)",
          "ระบบจะแสดง key ขึ้นต้นด้วย " + c("AIza") + " ยาวประมาณ 39 ตัวอักษร กด <b>Copy</b> แล้ววางเก็บไว้ในที่ปลอดภัย เช่น ไฟล์ Notes ส่วนตัว (ยังไม่ต้องวางลงในโค้ด)")
     + box("warn", "กติกาเรื่อง key — สำคัญมาก",
           ul("key = เงินของคุณ ใครได้ key ไปก็ใช้โควตาแทนคุณได้ <b>ห้ามโพสต์ในกลุ่ม ห้ามใส่ในสไลด์ ห้าม commit ขึ้น GitHub</b>",
              "แอปนี้ออกแบบให้ใส่ key ผ่านหน้า \"ตั้งค่า\" และเก็บไว้ในเครื่องเท่านั้น จึงไม่มี key อยู่ในโค้ดเลย",
              "ถ้าเผลอหลุด ให้กลับไปที่ aistudio.google.com/apikey กด <b>Delete</b> key เดิมแล้วสร้างใหม่ ใช้เวลาไม่ถึงนาที",
              "Google จำกัดโควตาฟรี \"ต่อนาที\" และ \"ต่อวัน\" (ดูตัวเลขปัจจุบันที่ aistudio.google.com/rate-limit) ถ้ากดถี่ ๆ จะได้ error 429 — รอสักครู่แล้วลองใหม่"))
     + h3("1.2 ยิงคำขอแรกด้วย curl (ยังไม่ต้องใช้ Flutter)")
     + p("เราจะคุยกับ Gemini ด้วยคำสั่ง " + c("curl") + " ก่อน เพื่อให้เห็นว่า \"API\" ก็คือการส่ง JSON ไปที่ URL หนึ่ง แล้วได้ JSON กลับมา — แอป Flutter ของเราก็จะทำแบบเดียวกันเป๊ะ (Windows 10/11 มี curl ติดมาแล้ว เปิด <b>PowerShell</b> หรือ Terminal ใน " + AS + " ก็ได้ · macOS เปิด Terminal)")
     + p("<b>macOS / Linux</b> (แทน " + c("ใส่KEYของคุณ") + " ด้วย key จริง):")
     + code('''curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent" \\
  -H "x-goog-api-key: ใส่KEYของคุณ" \\
  -H "Content-Type: application/json" \\
  -d '{"contents":[{"parts":[{"text":"มีไข่กับหมูสับ ทำอะไรกินได้บ้าง ตอบสั้นๆ"}]}]}\'''', "bash")
     + p("<b>Windows PowerShell</b> (ต้องใช้ " + c("curl.exe") + " เพราะ " + c("curl") + " เฉย ๆ ใน PowerShell เป็นคำสั่งอื่น และต้องใส่ body ผ่านไฟล์เพื่อเลี่ยงปัญหาเครื่องหมายคำพูด):")
     + code('''# 1) สร้างไฟล์ body.json ด้วย Notepad ให้มีข้อความนี้ (บันทึกเป็น UTF-8)
{"contents":[{"parts":[{"text":"มีไข่กับหมูสับ ทำอะไรกินได้บ้าง ตอบสั้นๆ"}]}]}

# 2) รันใน PowerShell ที่โฟลเดอร์เดียวกับ body.json
curl.exe "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent" -H "x-goog-api-key: ใส่KEYของคุณ" -H "Content-Type: application/json; charset=utf-8" --data-binary "@body.json"''', "bash")
     + p("ถ้าสำเร็จจะได้ JSON ก้อนใหญ่ หน้าตาประมาณนี้ (ตัดให้สั้น):")
     + code('''{
  "candidates": [
    {
      "content": {
        "parts": [ { "text": "ทำได้หลายเมนูเลยครับ เช่น\\n1. ไข่เจียวหมูสับ ..." } ],
        "role": "model"
      },
      "finishReason": "STOP"
    }
  ],
  "usageMetadata": { "promptTokenCount": 21, "candidatesTokenCount": 180, "totalTokenCount": 201 },
  "modelVersion": "gemini-3.8-flash"
}''', "json")
     + box("learn", "อ่าน JSON นี้ให้ออก — ทั้งแอปใช้แค่นี้",
           ul(c("candidates[0].content.parts[0].text") + " = ข้อความคำตอบ (คำตอบอาจแบ่งเป็นหลาย part ต้องเอามาต่อกัน)",
              c("finishReason") + " = ทำไมถึงหยุดตอบ: " + c("STOP") + " ปกติ · " + c("MAX_TOKENS") + " ยาวเกินที่กำหนด · " + c("SAFETY") + " ถูกบล็อก",
              c("usageMetadata") + " = ใช้ไปกี่ token (หน่วยนับความยาวข้อความ ประมาณ 1 token ≈ 1–3 ตัวอักษรไทย) — ตัวเลขนี้คือสิ่งที่โควตานับ",
              "ถ้าได้ " + c('{"error": {"code": 400, "message": "API key not valid..."}}') + " แปลว่า key ผิด/คัดลอกไม่ครบ · " + c("429") + " = ยิงถี่เกินโควตา"))
     + box("check", "Checkpoint 1",
           ul("มี API key เก็บไว้แล้ว และรู้ว่าจะไปลบ/สร้างใหม่ที่ไหน",
              "curl ได้คำตอบภาษาไทยจาก Gemini (ถ่ายภาพหน้าจอผลลัพธ์ไว้ส่งงาน)",
              "ชี้ได้ว่าข้อความคำตอบอยู่ตรงไหนของ JSON")))

# ================================================================ STEP 2
step(2, "โหลดโค้ดเริ่มต้น เปิดใน Android Studio และรันครั้งแรก", 25,
     "แอปรันบนอีมูเลเตอร์ได้ เห็นทุกหน้าในโหมดสาธิต และรู้ว่าเทสต์ไหนยัง fail (คือสิ่งที่ต้องทำ)",
     p("โค้ดเริ่มต้น (tag " + c(START_TAG) + ") มี UI ทุกหน้า โมเดลข้อมูล การตั้งค่า โหมดสาธิต และเทสต์ครบแล้ว <b>เว้นไว้เฉพาะส่วน \"คุยกับ AI\"</b> ใน 4 ไฟล์ ซึ่งคุณจะเขียนเองใน Step 5–7 (ค้นหาคำว่า " + c("TODO(Step") + " ในโปรเจกต์จะเจอทุกจุด)")
     + h3("2.1 โหลดโค้ด")
     + table(["วิธี", "ทำอย่างไร"], [
         ["git (แนะนำ)", code(f"git clone {REPO}.git kitchen_ai\ncd kitchen_ai\ngit checkout {START_TAG}\nflutter pub get", "bash")],
         ["ใน " + AS, "<b>File → New → Project from Version Control</b> → วาง URL " + c(REPO + ".git") + " → Clone แล้วไปที่ <b>Git → Branches… → Tags → " + START_TAG + " → Checkout</b>"],
         ["ZIP (ไม่ใช้ git)", "ดาวน์โหลด " + c(f"{REPO}/archive/refs/tags/{START_TAG}.zip") + " แตกไฟล์ แล้ว <b>File → Open</b> โฟลเดอร์ที่แตกออกมา"],
     ])
     + p("เปิดโปรเจกต์แล้วรอให้ " + AS + " ทำ " + c("flutter pub get") + " จนเสร็จ (มุมล่างขวามีแถบความคืบหน้า) ถ้ามันไม่ทำเอง เปิดไฟล์ " + c("pubspec.yaml") + " แล้วกด <b>Pub get</b> ที่แถบด้านบน")
     + h3("2.2 แพ็กเกจที่ใช้")
     + code(between(src_at(START_TAG, "pubspec.yaml"), "dependencies:", "dev_dependencies:"), "yaml", "pubspec.yaml", note="เฉพาะส่วน dependencies")
     + table(["แพ็กเกจ", "ใช้ทำอะไร", "เคยใช้ใน LabStock?"], [
         [c("http"), "ยิง HTTP POST ไป Gemini", "ใช่ (เรียก PHP API)"],
         [c("image_picker"), "ถ่ายรูป / เลือกรูปจากคลัง", "ใช่ (อัปโหลดรูปอุปกรณ์)"],
         [c("shared_preferences"), "เก็บ API key และโหมดสาธิตไว้ในเครื่อง", "ใช่ (จำการเข้าสู่ระบบ)"],
     ])
     + p("สังเกตว่า<b>ไม่มีแพ็กเกจ AI พิเศษ</b>เลย — เราคุยกับ Gemini ด้วย HTTP + JSON ล้วน ๆ เหมือนที่คุยกับ PHP ใน LabStock ต่างกันแค่ URL และรูปแบบ JSON เท่านั้น นี่คือจุดประสงค์ของแล็บนี้: ให้เห็นว่า \"AI API\" ไม่ได้มีเวทมนตร์อะไร")
     + h3("2.3 รันครั้งแรก")
     + ol("เปิด Device Manager สร้าง/เปิดอีมูเลเตอร์ (Pixel อะไรก็ได้ API 34 ขึ้นไป) หรือเสียบมือถือจริงที่เปิด USB debugging",
          "กด <b>Run ▶</b> (หรือ " + c("flutter run") + ") รอ build ครั้งแรก 2–5 นาที",
          "หน้าแรกจะมีแถบเหลืองเตือนว่า \"ยังไม่ได้ใส่ Gemini API key\" กด <b>ไปตั้งค่า</b>",
          "เปิดสวิตช์ <b>โหมดสาธิต</b> → กด <b>ทดสอบการเชื่อมต่อ</b> (ได้ข้อความจำลอง) → <b>บันทึก</b>",
          "ลองกด \"พิมพ์วัตถุดิบที่มี\" พิมพ์ ไข่ แล้วกด + → กด \"ให้ AI แนะนำเมนู\" — ใน starter จะขึ้น SnackBar ว่า <i>ยังไม่ได้เขียน _ask()</i> นั่นถูกต้องแล้ว เพราะคุณยังไม่ได้ทำ Step 6")
     + fig(("01_home_no_key", "หน้าแรกตอนยังไม่มี key"), ("02_settings", "หน้าตั้งค่า"), ("04_home_demo", "เปิดโหมดสาธิตแล้ว"))
     + h3("2.4 รันเทสต์ดูว่าอะไร \"ยังไม่เสร็จ\"")
     + p("โปรเจกต์มีเทสต์อัตโนมัติ 12 ข้อ ใน starter จะ <b>fail 7 ข้อ</b> ซึ่งก็คือ 7 สิ่งที่คุณต้องทำให้ผ่าน ใช้มันเป็นเช็กลิสต์ได้เลย:")
     + code("flutter test", "bash")
     + table(["ไฟล์เทสต์", "ใน starter", "จะผ่านเมื่อทำ"], [
         [c("test/gemini_client_test.dart") + " 6 ข้อ", "fail 5 / ผ่าน 1", "Step 5 (ข้อ \"ไม่มี key\" ผ่านตั้งแต่แรกเพราะเช็กไว้ให้แล้ว)"],
         [c("test/widget_test.dart") + " 6 ข้อ", "fail 2 / ผ่าน 4", "Step 6 (2 ข้อที่กดปุ่มขอเมนู)"],
     ])
     + box("learn", "ทำไมต้องมีโหมดสาธิต",
           ul("ให้ดู UI ได้ทันทีโดยไม่ต้องมี key / ไม่ต้องต่อเน็ต และไม่กินโควตา",
              "ให้เทสต์รันได้เร็วและเหมือนเดิมทุกครั้ง (AI จริงตอบไม่เหมือนเดิม จึงเทสต์อัตโนมัติยาก)",
              "ในโค้ดทำด้วย " + c("abstract class AiService") + " ที่มี 2 implementation: " + c("GeminiAiService") + " (จริง) และ " + c("DemoAiService") + " (จำลอง) หน้าจอไม่รู้เลยว่าคุยกับตัวไหน — เทคนิคเดียวกับ FakeApiService ใน LabStock"))
     + box("check", "Checkpoint 2",
           ul("แอปรันบนอีมูเลเตอร์ เปิดโหมดสาธิตแล้วเห็นหน้าตั้งค่าตอบข้อความจำลอง",
              c("flutter test") + " ได้ผล 5 passed, 7 failed (ตัวเลขนี้คือจุดเริ่มต้น)")))

# ================================================================ STEP 3
step(3, "ทัวร์โค้ดที่ให้มา: ข้อมูลไหลจากหน้าจอไปถึง Gemini อย่างไร", 30,
     "วาดภาพในหัวได้ว่าแต่ละไฟล์ทำหน้าที่อะไร และจุดที่ต้องเขียนเองอยู่ตรงไหนของเส้นทาง",
     p("แอปแบ่งเป็น 3 ชั้น เหมือน LabStock (screens → AppState/ApiService → เซิร์ฟเวอร์) เปลี่ยนแค่ปลายทางจาก PHP เป็น Gemini:")
     + code('''หน้าจอ (screens/)            งานของแอป (data/ai_service.dart)        คุยกับ Gemini (data/gemini_client.dart)
┌──────────────────────┐    ┌──────────────────────────────┐    ┌──────────────────────────────┐
│ IngredientsScreen    │───▶│ AiService.suggestMenus(list) │───▶│ GeminiClient.generate(       │
│  "ไข่, หมูสับ"        │    │  • ประกอบ prompt + schema     │    │   prompt, systemInstruction, │   HTTPS
│                      │◀───│  • แปลง JSON → MenuResult     │◀───│   imageBytes?, responseSchema)│◀────────▶ Gemini API
│ PhotoScreen          │───▶│ AiService.analyzePhoto(bytes)│───▶│  • ประกอบ body JSON           │
│  รูป (bytes)          │    │  • แปลง JSON → PhotoAnalysis  │    │  • POST + header x-goog-api-key│
└──────────────────────┘    └──────────────────────────────┘    │  • ตรวจ status, แกะ text       │
                                      ▲                          └──────────────────────────────┘
                              AppSettings (data/app_settings.dart) เลือกว่าใช้ GeminiAiService หรือ DemoAiService''', "text")
     + table(["ไฟล์", "หน้าที่", "สถานะใน starter"], [
         [c("lib/main.dart"), "สร้าง AppSettings โหลดค่าจากเครื่อง แล้วเปิด HomeScreen", "เสร็จ"],
         [c("lib/theme.dart"), "สีและสไตล์ปุ่ม/ช่องกรอก", "เสร็จ"],
         [c("lib/data/ai_config.dart"), "ชื่อโมเดล, URL, timeout — ค่าคงที่ที่อาจต้องแก้ในอนาคต", "เสร็จ"],
         [c("lib/data/gemini_client.dart"), "ส่ง HTTP ไป Gemini และแกะคำตอบ (ไม่รู้จักเรื่องอาหารเลย)", "<b>TODO Step 5</b>"],
         [c("lib/data/prompts.dart"), "ข้อความ prompt และ JSON schema ที่ให้ AI ตอบ", "เสร็จ (จะได้ปรับใน Step 6)"],
         [c("lib/data/ai_service.dart"), "งานของแอป: suggestMenus / analyzePhoto / ping (+ โหมดสาธิต)", "<b>TODO Step 6, 7</b>"],
         [c("lib/data/app_settings.dart"), "เก็บ key + โหมดสาธิต, สร้าง AiService ให้หน้าจอ", "เสร็จ"],
         [c("lib/models/*.dart"), "คลาสข้อมูล MenuSuggestion, MenuResult, FoundItem, PhotoAnalysis (fromJson)", "เสร็จ"],
         [c("lib/screens/home_screen.dart"), "หน้าแรก + แบนเนอร์เตือน key", "เสร็จ"],
         [c("lib/screens/settings_screen.dart"), "ใส่ key, โหมดสาธิต, ปุ่มทดสอบ", "เสร็จ"],
         [c("lib/screens/ingredients_screen.dart"), "chips วัตถุดิบ → ขอเมนู → MenuCard", "<b>TODO Step 6</b> (_ask)"],
         [c("lib/screens/photo_screen.dart"), "เลือกรูป → วิเคราะห์ → ส่งต่อ", "<b>TODO Step 7</b> (_pickImage, _analyze)"],
         [c("lib/widgets/*.dart"), "MenuCard (การ์ดขยายได้), ErrorBox (error + ลองใหม่)", "เสร็จ"],
     ])
     + h3("3.1 ค่าคงที่: ai_config.dart")
     + file_block("lib/data/ai_config.dart", START_TAG)
     + p("ชื่อโมเดลของ Google เปลี่ยนทุกไม่กี่เดือน ถ้าวันหนึ่งแอปขึ้น error 404 \"ไม่พบโมเดล\" ให้เปิดหน้า https://ai.google.dev/gemini-api/docs/models เลือกโมเดลตระกูล Flash ที่ยังอยู่ แล้วแก้ที่บรรทัดเดียวนี้")
     + h3("3.2 โมเดลข้อมูล: แปลง JSON เป็น object")
     + part_block("lib/models/menu_suggestion.dart", "class MenuSuggestion {", "static List<String> _stringList", tag=START_TAG, note="ส่วน MenuSuggestion")
     + p("รูปแบบเดียวกับ " + c("Equipment.fromJson") + " ใน LabStock ต่างตรงที่ JSON มาจาก AI ไม่ใช่ฐานข้อมูล จึง<b>ป้องกันค่าหายทุกช่อง</b> (" + c("?? ''") + ", " + c("?? const []") + ") เพราะ AI อาจตอบไม่ครบแม้เราจะกำหนด schema ไว้ก็ตาม")
     + h3("3.3 การตั้งค่า: app_settings.dart")
     + part_block("lib/data/app_settings.dart", "class AppSettings extends ChangeNotifier", "/// โหลดค่าที่เคยบันทึกไว้", tag=START_TAG, note="ส่วนบน")
     + box("learn", "จุดสำคัญในไฟล์นี้",
           ul(c("aiService") + " สร้าง " + c("GeminiAiService(GeminiClient(apiKey: _apiKey))") + " ใหม่ทุกครั้งที่ถูกเรียก จึงได้ key ล่าสุดเสมอ ไม่ต้องรีสตาร์ตแอปหลังเปลี่ยน key",
              c("ready") + " = มี key หรือเปิดโหมดสาธิต → HomeScreen ใช้ตัดสินใจว่าจะโชว์แถบเตือนไหม",
              "เป็น " + c("ChangeNotifier") + " และ HomeScreen ครอบด้วย " + c("ListenableBuilder") + " → บันทึกค่าปุ๊บหน้าแรกวาดใหม่ปั๊บ"))
     + h3("3.4 หน้าจอเรียก AI อย่างไร (ดูจากหน้าตั้งค่าที่เสร็จแล้ว)")
     + part_block("lib/screens/settings_screen.dart", "/// ส่งคำถามสั้น ๆ เพื่อเช็กว่า key ใช้ได้", "@override\n  Widget build", tag=START_TAG, note="เมธอด _test()")
     + p("นี่คือ<b>แม่แบบ</b>ของทุกเมธอดที่คุยกับ AI ในแอป จำโครงนี้ไว้ จะได้ใช้ซ้ำใน Step 6 และ 7:")
     + ol("setState เปิดสถานะ \"กำลังโหลด\" และล้างผลเก่า",
          c("await") + " เรียก AiService ใน " + c("try"),
          c("on AiException") + " → เก็บ " + c("e.message") + " (ข้อความภาษาไทยพร้อมแสดง)",
          c("finally") + " → ปิดสถานะโหลด",
          "<b>เช็ก " + c("mounted") + " ก่อน setState ทุกครั้งหลัง await</b> — ผู้ใช้อาจกดย้อนกลับไปแล้วระหว่างรอ AI (ซึ่งนานหลายวินาที)")
     + box("check", "Checkpoint 3",
           ul("บอกได้ว่าเมื่อผู้ใช้กด \"ให้ AI แนะนำเมนู\" โค้ดจะวิ่งผ่านไฟล์ไหนบ้างตามลำดับ",
              "เปิดไฟล์ 4 ไฟล์ที่มี TODO และอ่านคอมเมนต์ TODO ทุกจุดแล้ว")))

# ================================================================ STEP 4
step(4, "เข้าใจ Gemini API: JSON ที่ส่งไป และ JSON ที่ได้กลับมา", 25,
     "อ่าน/เขียน request และ response ของ generateContent ได้ทุกช่อง ก่อนลงมือเขียนโค้ด",
     p("Gemini มี REST API ชื่อ " + c("generateContent") + " ทำงานแบบ \"ส่ง JSON ไป ได้ JSON กลับ\" ครั้งเดียวจบ (ไม่จำบทสนทนา — ถ้าอยากคุยต่อเนื่องต้องส่งประวัติไปเองทุกครั้ง ดูโจทย์ท้าทายข้อ B) URL มีรูปแบบคงที่:")
     + code("POST https://generativelanguage.googleapis.com/v1beta/models/{ชื่อโมเดล}:generateContent\n"
            "Header  x-goog-api-key: <API key>\n"
            "Header  Content-Type: application/json", "text")
     + h3("4.1 Request: สิ่งที่เราส่งไป")
     + code('''{
  "system_instruction": {                       // (ไม่บังคับ) บทบาท/กติกาที่ AI ต้องยึดตลอด
    "parts": [ { "text": "คุณคือเชฟอาหารไทย ตอบเป็นภาษาไทย ..." } ]
  },
  "contents": [                                 // บทสนทนา — แล็บนี้ส่งแค่ 1 ข้อความจากผู้ใช้
    {
      "role": "user",
      "parts": [                                // 1 ข้อความมีหลาย "ชิ้น" ได้: ข้อความ + รูป
        { "text": "ตอนนี้ฉันมี ไข่, หมูสับ ..." },
        { "inline_data": { "mime_type": "image/jpeg", "data": "<รูปเข้ารหัส base64>" } }
      ]
    }
  ],
  "generationConfig": {                         // ตัวเลือกการตอบ
    "temperature": 0.7,                         // 0 = ตอบนิ่ง ๆ เหมือนเดิม · 1-2 = สร้างสรรค์/สุ่มมากขึ้น
    "maxOutputTokens": 8192,                    // เพดานความยาวคำตอบ
    "thinkingConfig": { "thinkingLevel": "low" },// Gemini 3.x "คิดก่อนตอบ" ค่าเริ่มต้น medium ช้ามาก → ลดเป็น low
    "responseMimeType": "application/json",     // (ไม่บังคับ) บังคับให้ตอบเป็น JSON ล้วน
    "responseSchema": { "type": "object", ... } // (ไม่บังคับ) โครงสร้าง JSON ที่ต้องการ
  }
}''', "json", note="คอมเมนต์ // ใส่ไว้เพื่ออธิบาย JSON จริงห้ามมี")
     + table(["ช่อง", "เขียนอย่างไร", "ทำไมสำคัญ"], [
         [c("system_instruction"), "ข้อความบอกบทบาท กติกา ภาษา รูปแบบ", "เขียนครั้งเดียวใช้กับทุกคำถาม ทำให้คำตอบนิ่งและเป็นแนวเดียวกัน (ของเราอยู่ใน prompts.dart)"],
         [c("contents[].parts[]"), "อาร์เรย์ของ " + c("{text}") + " หรือ " + c("{inline_data}"), "ส่งรูปกับข้อความไปพร้อมกันได้ = multimodal · รูปต้องเป็น base64 ไม่ใช่ URL"],
         [c("temperature"), "0–2", "งาน \"ดูรูปแล้วบอกว่ามีอะไร\" ใช้ค่าต่ำ (0.2) · งาน \"คิดเมนู\" ใช้ 0.7 ให้มีความหลากหลาย"],
         [c("thinkingConfig.thinkingLevel"), c("low") + " / " + c("medium") + " / " + c("high"), "โมเดล Gemini 3.x จะ \"คิดในใจ\" ก่อนตอบ ยิ่งระดับสูงยิ่งฉลาดแต่ช้าและกิน token — งานแนะนำเมนูใช้ low พอ (ไม่ใส่ = medium ซึ่งเคยรอเกิน 90 วินาที)"],
         [c("responseSchema"), "JSON Schema แบบย่อ (type/properties/items/required/enum)", "ไม่ต้องเขียน regex แกะคำตอบ — AI ตอบตรงโครงสร้าง แปลงด้วย " + c("jsonDecode") + " ได้เลย"],
     ])
     + box("learn", "ทำไม key ต้องอยู่ใน header ไม่ใช่ใน URL",
           ul("เอกสารเก่าของ Google ใส่ " + c("?key=...") + " ท้าย URL ซึ่งใช้ได้ แต่ URL มักถูกบันทึกใน log ของเซิร์ฟเวอร์ proxy และประวัติต่าง ๆ ทำให้ key รั่วง่าย",
              "header " + c("x-goog-api-key") + " เป็นวิธีที่ Google แนะนำในปัจจุบัน และเทสต์ของเราตรวจว่า key <b>ต้องไม่</b>อยู่ใน URL"))
     + h3("4.2 Response: สิ่งที่ได้กลับมา")
     + code('''{
  "candidates": [                               // คำตอบ (ปกติมี 1 ตัว)
    {
      "content": { "role": "model", "parts": [ { "text": "{\\"summary\\": \\"...\\", \\"menus\\": [...]}" } ] },
      "finishReason": "STOP"                    // STOP · MAX_TOKENS · SAFETY · RECITATION ...
    }
  ],
  "promptFeedback": { "blockReason": "SAFETY" },// มีเฉพาะตอน "คำถาม" ถูกบล็อก (แล้ว candidates จะว่าง)
  "usageMetadata": { "promptTokenCount": 310, "candidatesTokenCount": 820, "totalTokenCount": 1130 },
  "modelVersion": "gemini-3.8-flash"
}''', "json")
     + p("สังเกตว่าเมื่อเราขอ " + c("responseMimeType: application/json") + " ค่าใน " + c("text") + " จะเป็น<b>สตริง JSON</b> (JSON ซ้อนใน JSON) เราจึงต้อง " + c("jsonDecode") + " สองชั้น: ชั้นแรกแกะ response ทั้งก้อน (ทำใน GeminiClient) ชั้นสองแกะข้อความคำตอบเป็น MenuResult (ทำใน AiService)")
     + h3("4.3 เมื่อผิดพลาด")
     + table(["HTTP", "body ที่ได้", "สาเหตุที่พบบ่อย", "แอปควรบอกผู้ใช้ว่า"], [
         ["400", c('{"error":{"code":400,"message":"API key not valid..."}}'), "key ผิด / คัดลอกไม่ครบ / ถูกลบไปแล้ว", "ตรวจ key ที่หน้าตั้งค่า"],
         ["400", c('"message":"Invalid JSON payload..."'), "body ผิดรูปแบบ (สะกดชื่อช่องผิด)", "บั๊กของเรา ดู message แล้วแก้"],
         ["403", c('"status":"PERMISSION_DENIED"'), "key ไม่มีสิทธิ์ใช้ API นี้ / ประเทศไม่รองรับ", "สร้าง key ใหม่"],
         ["404", c('"status":"NOT_FOUND"'), "ชื่อโมเดลผิดหรือถูกปลดระวาง", "แก้ kGeminiModel"],
         ["429", c('"status":"RESOURCE_EXHAUSTED"'), "ยิงเกินโควตาฟรีต่อนาที/ต่อวัน", "รอสักครู่ · เปลี่ยนไปโมเดล lite"],
         ["503", c('"status":"UNAVAILABLE"'), "เซิร์ฟเวอร์ Google คนเยอะ", "ลองใหม่"],
         ["200 แต่ candidates ว่าง", c('"promptFeedback":{"blockReason":"SAFETY"}'), "คำถาม/รูปเข้าข่ายไม่เหมาะสม", "เปลี่ยนคำถาม"],
     ])
     + p("ทุกกรณีในตารางถูกแปลงเป็นภาษาไทยไว้แล้วใน " + c("GeminiClient.describeHttpError()") + " (ให้มาใน starter) หน้าที่ของคุณใน Step 5 คือ<b>เรียกใช้</b>มันให้ถูกจังหวะ")
     + box("check", "Checkpoint 4",
           ul("เขียน body JSON สำหรับถามว่า \"ไข่ 2 ฟอง ทำอะไรได้บ้าง\" ด้วยมือได้โดยไม่เปิดดู",
              "บอกได้ว่า JSON ซ้อน 2 ชั้นคืออะไร และแต่ละชั้นถูกแกะที่ไฟล์ไหน")))

# ================================================================ STEP 5
step(5, "เขียน GeminiClient: ส่งคำขอและแกะคำตอบ", 50,
     "generate() ยิง HTTP ไป Gemini ได้จริง · extractText() แกะข้อความได้ · เทสต์ 6 ข้อผ่าน · ปุ่ม \"ทดสอบการเชื่อมต่อ\" ได้คำตอบจาก Gemini จริง",
     p("เปิด " + c("lib/data/gemini_client.dart") + " ใน starter คุณจะเห็นโครงนี้ (ตัดส่วน helper ออก):")
     + part_block("lib/data/gemini_client.dart", "  Future<String> generate({", "  /// แปลงรหัสสถานะ HTTP", tag=START_TAG, note="starter · ส่วนที่ต้องเขียน")
     + p("สิ่งที่ให้มาแล้วในไฟล์: คลาส " + c("AiException") + ", constructor ที่รับ " + c("http.Client") + " (เพื่อให้เทสต์สวมเซิร์ฟเวอร์ปลอมได้), " + c("endpoint") + ", " + c("describeHttpError()") + " และการเช็ก key ว่าง ลบคอมเมนต์ TODO และบรรทัด " + c("throw UnimplementedError") + " ออก แล้วเขียนทีละข้อตามนี้")
     + h3("5.1 ประกอบ parts")
     + part_block("lib/data/gemini_client.dart", "    // 1) ประกอบ \"ชิ้นส่วน\" ของคำถาม", "    // 2) ประกอบ body", note="1/5")
     + ul("ใช้ <b>collection if</b> (" + c("if (imageBytes != null) {...}") + " ข้างใน list) จะได้ไม่ต้องสร้าง list แล้ว add ทีหลัง",
          c("base64Encode") + " มาจาก " + c("dart:convert") + " แปลง bytes ของรูปเป็นข้อความ ASCII ยาว ๆ — รูป 100 KB จะกลายเป็นข้อความ ~133 KB นี่คือเหตุผลที่หน้ารูปต้องย่อรูปก่อนส่ง")
     + h3("5.2 ประกอบ body")
     + part_block("lib/data/gemini_client.dart", "    // 2) ประกอบ body", "    // 3) ยิง HTTP POST", note="2/5")
     + ul("เทียบกับ JSON ใน Step 4.1 ทีละช่อง ชื่อช่องต้องสะกดเป๊ะ (Gemini รับทั้ง " + c("system_instruction") + " และ " + c("systemInstruction") + " แต่ " + c("generationConfig") + " ต้องเป็น camelCase)",
          c("thinkingConfig") + " อ่านจาก " + c("kThinkingLevel") + " ใน ai_config.dart — ถ้าตอบช้าหรือเร็วไป แก้ที่เดียว",
          "ใช้ collection if อีกครั้งเพื่อใส่ " + c("responseMimeType") + "/" + c("responseSchema") + " เฉพาะตอนที่ผู้เรียกส่ง schema มา — ถ้าใส่ " + c("responseSchema: null") + " ไป Gemini จะตอบ 400")
     + h3("5.3 ยิง HTTP POST และดักข้อผิดพลาดระดับเครือข่าย")
     + part_block("lib/data/gemini_client.dart", "    // 3) ยิง HTTP POST", "    // 4) ตรวจสถานะ HTTP", note="3/5")
     + ul(c("jsonEncode(body)") + " แปลง Map เป็นสตริง JSON · header " + c("Content-Type") + " บอกว่า body เป็น JSON",
          c(".timeout(kAiTimeout)") + " สำคัญมาก: AI ใช้เวลาตอบ 3–20 วินาที ถ้าเน็ตหลุดกลางทาง ไม่มี timeout แอปจะหมุนค้างตลอดกาล",
          "ดัก 3 แบบ: หมดเวลา (" + c("TimeoutException") + " จาก dart:async) · ไม่มีเน็ต (" + c("SocketException") + " จาก dart:io) · อื่น ๆ ของ package http (" + c("http.ClientException") + ") แล้ว<b>แปลงทั้งหมดเป็น AiException</b> หน้าจอจึงดักแค่ชนิดเดียว")
     + h3("5.4 ตรวจสถานะ HTTP")
     + part_block("lib/data/gemini_client.dart", "    // 4) ตรวจสถานะ HTTP", "    // 5) แกะข้อความ", note="4/5")
     + h3("5.5 แกะข้อความ")
     + part_block("lib/data/gemini_client.dart", "    // 5) แกะข้อความ", "  /// แปลงรหัสสถานะ HTTP", note="5/5")
     + h3("5.6 extractText(): เดินเข้าไปใน JSON ให้ปลอดภัย")
     + part_block("lib/data/gemini_client.dart", "  static String extractText(", None, note="ทั้งเมธอด")
     + box("learn", "อ่านโค้ด extractText ทีละบรรทัด",
           ul("ทุกชั้นใช้ " + c("as ...?") + " (nullable cast) แล้วเช็ก null — เพราะ JSON จาก AI ไม่มีการันตีว่าช่องไหนจะมี การ cast ตรง ๆ แบบ " + c("json['candidates'][0]") + " จะพังทันทีที่ช่องหาย",
              c("first['content']?['parts']") + " — เครื่องหมาย " + c("?") + " หลัง " + c("['content']") + " คือ null-aware index: ถ้า content เป็น null ให้ทั้งนิพจน์เป็น null แทนที่จะ crash",
              c(".whereType<String>()") + " กรองเอาเฉพาะ part ที่เป็นข้อความ (part ชนิดอื่นเช่น thought/functionCall จะถูกข้าม) แล้ว " + c(".join()") + " ต่อกัน",
              "ลำดับการเช็ก: ถูกบล็อก → ไม่มี candidates → ข้อความว่าง แต่ละกรณีให้ข้อความ error ต่างกัน ผู้ใช้จะได้รู้ว่าควรทำอะไรต่อ"))
     + h3("5.7 ทดสอบด้วยเซิร์ฟเวอร์ปลอม")
     + p("ไฟล์ " + c("test/gemini_client_test.dart") + " ใช้ " + c("MockClient") + " จาก package http สวมเป็น Gemini — มันจับ request ที่โค้ดคุณสร้างมาตรวจทีละช่อง และตอบ JSON ที่เรากำหนดเองได้ (รวมถึง 429) จึงทดสอบทุกเงื่อนไขได้โดยไม่ใช้โควตาแม้แต่ token เดียว")
     + part_block("test/gemini_client_test.dart", "  test('ส่ง header x-goog-api-key", "  test('แนบรูปเป็น inline_data", tag=START_TAG, note="เทสต์ข้อแรก")
     + code("flutter test test/gemini_client_test.dart", "bash")
     + p("ต้องได้ <b>All tests passed!</b> (6 ข้อ) ถ้าข้อไหน fail ให้อ่านบรรทัด " + c("Expected:") + " / " + c("Actual:") + " ในผลลัพธ์ มันบอกชัดว่าช่องไหนของ JSON ไม่ตรง")
     + h3("5.8 ทดสอบกับ Gemini จริง")
     + ol("รันแอป → ตั้งค่า → <b>ปิด</b>โหมดสาธิต → วาง API key → กด <b>ทดสอบการเชื่อมต่อ</b>",
          "ควรได้ประโยคทักทายภาษาไทยพร้อมชื่อโมเดลภายใน 2–5 วินาที (เมธอด " + c("ping()") + " ใน ai_service.dart เรียก " + c("generate()") + " ที่คุณเพิ่งเขียน)",
          "ลองพิมพ์ key ผิด 1 ตัวแล้วทดสอบอีกครั้ง → ต้องได้ข้อความ \"API key ไม่ถูกต้อง...\" ไม่ใช่แอป crash",
          "ปิด Wi-Fi ของอีมูเลเตอร์ (แถบด้านข้าง → … → Cellular/Wi-Fi) แล้วทดสอบ → ต้องได้ \"เชื่อมต่ออินเทอร์เน็ตไม่ได้\"")
     + fig(("03_settings_demo_ok", "ผลทดสอบการเชื่อมต่อ (ภาพจากโหมดสาธิต — ของจริงจะเป็นคำทักทายจาก Gemini)"))
     + box("check", "Checkpoint 5",
           ul(c("flutter test test/gemini_client_test.dart") + " ผ่าน 6/6",
              "ปุ่มทดสอบการเชื่อมต่อได้คำตอบจาก Gemini จริง (ถ่ายภาพหน้าจอไว้)",
              "key ผิดและไม่มีเน็ตได้ข้อความภาษาไทยที่ถูกต้อง ไม่ crash")),
     kind="ทำเอง")

# ================================================================ STEP 6
step(6, "หน้า \"เมนูจากวัตถุดิบ\": prompt, JSON schema และการแสดงผล", 45,
     "พิมพ์วัตถุดิบ → กดปุ่ม → ได้การ์ดเมนู 3 รายการจาก Gemini จริง พร้อมวัตถุดิบ ของที่ต้องซื้อ และวิธีทำ",
     h3("6.1 อ่าน prompt ที่ให้มา (prompts.dart)")
     + part_block("lib/data/prompts.dart", "const String kChefSystemInstruction", "const Map<String, dynamic> kMenuResponseSchema", tag=START_TAG, note="system instruction + buildMenuPrompt")
     + box("learn", "หลักเขียน prompt ที่ใช้ในไฟล์นี้",
           ul("<b>บทบาท</b> (\"คุณคือเชฟ...\") ทำให้น้ำเสียงและความรู้ที่ดึงมาใช้ตรงงาน",
              "<b>กติกาเป็นข้อ ๆ</b> อ่านง่ายกว่าย่อหน้ายาว ๆ ทั้งคนและ AI",
              "<b>บอกข้อสมมติ</b> (ของพื้นฐานถือว่ามี) ลดการตอบว่า \"ต้องซื้อน้ำปลา\" ซึ่งไม่มีประโยชน์",
              "<b>ระบุจำนวนและลำดับ</b> (3 เมนู เรียงจากของครบที่สุด) คำตอบจะคงที่ เอาไปแสดงผลได้",
              "<b>แยก system กับ user</b>: ของที่คงที่ทุกครั้งไว้ใน system_instruction · ของที่เปลี่ยนตามผู้ใช้ (รายการวัตถุดิบ เงื่อนไข) ไว้ใน prompt"))
     + part_block("lib/data/prompts.dart", "const Map<String, dynamic> kMenuResponseSchema", "/// คำถามสำหรับให้ AI \"ดูรูป\"", tag=START_TAG, note="JSON schema ของคำตอบ")
     + p("Schema นี้คือ \"แบบฟอร์ม\" ที่ AI ต้องกรอก สังเกต " + c("description") + " ในแต่ละช่อง — AI อ่านมันด้วย จึงใช้บอกรูปแบบย่อย ๆ ได้ (เช่น \"ไข่ไก่ 2 ฟอง\") และ " + c("enum") + " จำกัดค่าให้เลือกได้แค่ 3 แบบ ซึ่งคลาส " + c("MenuSuggestion.fromJson") + " รับได้พอดี")
     + h3("6.2 เขียน GeminiAiService.suggestMenus()")
     + part_block("lib/data/ai_service.dart", "  Future<MenuResult> suggestMenus(List<String> ingredients, {String? extra}) async {", "  @override\n  Future<PhotoAnalysis>", note="เฉลย · ลบ TODO แล้วเขียนแบบนี้")
     + p("แค่ 3 บรรทัด: ประกอบ prompt → เรียก generate พร้อม schema → แปลงสตริง JSON เป็น MenuResult (" + c("fromJsonText") + " เรียก " + c("jsonDecode") + " ให้แล้ว นี่คือ JSON ชั้นที่สองจาก Step 4.2)")
     + h3("6.3 เขียน _ask() ในหน้าจอ")
     + part_block("lib/screens/ingredients_screen.dart", "  /// ส่งรายการวัตถุดิบไปถาม AI", "  @override\n  Widget build", note="เฉลย")
     + ul("โครงเดียวกับ " + c("_test()") + " ในหน้าตั้งค่า (Step 3.4) เพิ่ม " + c("catch (e)") + " ท้ายสุดดักกรณี AI ตอบ JSON เพี้ยนจน " + c("jsonDecode") + " พัง (" + c("FormatException") + ") — เกิดได้แม้มี schema เช่นตอนคำตอบยาวเกิน maxOutputTokens แล้วถูกตัดกลางคัน",
          "ส่วน build() ให้มาแล้ว: มันดูตัวแปร 3 ตัว " + c("_loading / _error / _result") + " แล้วเลือกวาด spinner / ErrorBox / การ์ดเมนู ตามลำดับ — คุณแค่ทำให้ตัวแปร 3 ตัวนี้มีค่าถูกต้อง")
     + h3("6.4 รันจริง")
     + ol("รันแอป (โหมดสาธิตปิด, key ใส่แล้ว) → \"พิมพ์วัตถุดิบที่มี\" → พิมพ์ " + c("ไข่, หมูสับ, กระเทียม") + " กด Enter (พิมพ์หลายอย่างคั่นด้วย , ได้) → เงื่อนไข \"ไม่กินเผ็ด\" → กดปุ่ม",
          "รอ 5–20 วินาที (มีตัวนับวินาทีให้ดูว่ายังทำงานอยู่) จะได้ 3 การ์ด การ์ดแรกขยายอยู่ กดการ์ดอื่นเพื่อขยาย สังเกตป้าย \"ของครบ\" / \"ซื้อเพิ่ม n\"",
          "กดปุ่มซ้ำ → คำตอบไม่เหมือนเดิม (temperature 0.7) ลองแก้เป็น 0 ใน " + c("generate(... temperature: ...)") + " ดูว่าต่างไหม",
          "ลบวัตถุดิบออกให้หมดแล้วกด → ต้องได้ SnackBar เตือน ไม่ยิงคำขอ")
     + fig(("06_ingredients_filled", "กรอกวัตถุดิบและเงื่อนไข"), ("07_ingredients_loading", "ระหว่างรอ AI"), ("08_ingredients_result", "ผลลัพธ์ (ภาพจากโหมดสาธิต)"))
     + h3("6.5 ทดลองแก้ prompt (ทำแล้วบันทึกผลส่งด้วย)")
     + table(["ทดลอง", "แก้ตรงไหน", "คาดว่าจะเห็น"], [
         ["ขอ 5 เมนู", "buildMenuPrompt: \"3 เมนู\" → \"5 เมนู\"", "การ์ด 5 ใบ (ช้าลงเล็กน้อย)"],
         ["ตอบเป็นอังกฤษ", "kChefSystemInstruction บรรทัดภาษา", "ชื่อเมนู/วิธีทำเป็นอังกฤษ แต่โครง JSON เหมือนเดิม"],
         ["เชฟอารมณ์ร้าย", "เพิ่มบุคลิกใน system instruction", "น้ำเสียงใน description เปลี่ยน — ตัวอย่างว่า system instruction มีอิทธิพลแค่ไหน"],
         ["ลบ responseSchema ออก", "suggestMenus: ไม่ส่ง responseSchema", "AI ตอบเป็น markdown ธรรมดา → fromJsonText พัง → เห็น \"อ่านคำตอบของ AI ไม่ได้\" (นี่คือเหตุผลที่ต้องมี schema)"],
     ])
     + box("check", "Checkpoint 6",
           ul(c("flutter test") + " ผ่านครบ 12/12 (เทสต์หน้าจอ 2 ข้อที่เคย fail ต้องผ่านแล้ว)",
              "ได้เมนูจาก Gemini จริงจากวัตถุดิบที่คุณพิมพ์เอง (ถ่ายภาพหน้าจอ 2 ภาพ: ก่อนกดและผลลัพธ์)",
              "บันทึกผลการทดลองแก้ prompt อย่างน้อย 2 ข้อ (แก้อะไร เห็นอะไร)")),
     kind="ทำเอง")

# ================================================================ STEP 7
step(7, "หน้า \"ถ่ายรูปวัตถุดิบ\": ส่งรูปให้ AI ดู", 45,
     "ถ่าย/เลือกรูป → AI บอกว่าเห็นอะไร → กดปุ่มส่งต่อไปขอเมนูจากของในรูป",
     p("ตอนนี้ท่อส่งข้อมูลพร้อมแล้ว (generate รับ imageBytes ได้ตั้งแต่ Step 5) เหลือแค่ 3 ชิ้น: เอารูปเข้ามา · ส่งไปวิเคราะห์ · แปลงผล")
     + h3("7.1 เขียน _pickImage(): เอารูปเข้ามาและย่อก่อน")
     + part_block("lib/screens/photo_screen.dart", "  /// เปิดกล้องหรือคลังรูป", "  static String _guessMime", note="เฉลย")
     + box("learn", "ทำไมต้องย่อรูป",
           ul("กล้องมือถือถ่ายได้รูป 3–8 MB · base64 ทำให้ใหญ่ขึ้นอีก 33% · Gemini จำกัดคำขอทั้งก้อนที่ 20 MB และยิ่งใหญ่ยิ่งช้าและกินโควตา token",
              c("maxWidth/maxHeight: 1024") + " + " + c("imageQuality: 80") + " ให้รูป ~100–300 KB ซึ่ง AI ดูออกสบาย ๆ (หน้าจอแสดงขนาดที่จะส่งให้ดูใต้รูป)",
              c("readAsBytes()") + " ได้ " + c("Uint8List") + " เก็บไว้ใน state ทั้งแสดงผล (" + c("Image.memory") + ") และส่งต่อโดยไม่ต้องอ่านไฟล์ซ้ำ",
              c("file.mimeType") + " บน Android บางครั้งเป็น null จึงมี " + c("_guessMime") + " เดาจากนามสกุล — Gemini ต้องการ mime_type ที่ถูกต้อง ไม่งั้นได้ 400"))
     + h3("7.2 เขียน _analyze()")
     + part_block("lib/screens/photo_screen.dart", "  /// ส่งรูปไปให้ AI วิเคราะห์", "  /// เอาชื่อของที่ AI เห็น", note="เฉลย")
     + p("โครงเดียวกับ " + c("_ask()") + " เป๊ะ ต่างแค่เรียก " + c("analyzePhoto") + " — ถ้าเขียน Step 6 ได้ ข้อนี้ควรใช้เวลาไม่ถึง 5 นาที")
     + h3("7.3 เขียน GeminiAiService.analyzePhoto()")
     + part_block("lib/data/ai_service.dart", "  Future<PhotoAnalysis> analyzePhoto(Uint8List imageBytes, {String mimeType = 'image/jpeg'}) async {\n    final text", "  @override\n  Future<String> ping()", note="เฉลย")
     + p("prompt และ schema สำหรับรูปอยู่ใน prompts.dart แล้ว (" + c("kPhotoPrompt") + ", " + c("kPhotoResponseSchema") + ") จุดต่างคือ " + c("temperature: 0.2") + " — การ \"บอกว่าเห็นอะไร\" ต้องการความแม่น ไม่ต้องการจินตนาการ")
     + h3("7.4 ทดสอบ")
     + ol("<b>บนอีมูเลเตอร์</b> กล้องเป็นฉากจำลอง 3 มิติ ให้ใช้ \"เลือกจากคลัง\" แทน: ลากไฟล์รูปอาหาร (หาจาก Google Images หรือถ่ายของในตู้เย็นแล้วส่งเข้าคอม) ไปวางบนหน้าต่างอีมูเลเตอร์ รูปจะไปอยู่ใน Downloads แล้วเลือกได้",
          "<b>บนมือถือจริง</b> กด \"ถ่ายรูป\" ถ่ายของในครัว/โต๊ะอาหาร — สนุกกว่าและเห็นความแม่นของ AI ชัด",
          "กด \"ให้ AI วิเคราะห์รูป\" รอ 5–15 วินาที จะได้คำบรรยาย + รายการของพร้อมปริมาณ",
          "กด \"แนะนำเมนูจากของ n อย่างนี้\" → เปิดหน้าเมนูโดยมี chips กรอกให้แล้ว (" + c("initialIngredients") + ") → กดขอเมนูต่อได้เลย",
          "ลองรูปที่ไม่ใช่อาหาร (เช่น รูปโน้ตบุ๊ก) → AI ควรบอกตามจริงและรายการว่าง (กติกานี้อยู่ใน kPhotoPrompt)")
     + fig(("10_photo_empty", "ก่อนเลือกรูป"), ("11_photo_picked", "เลือกรูปแล้ว (แสดงขนาด)"), ("12_photo_result", "ผลวิเคราะห์ (โหมดสาธิต)"), ("13_photo_to_ingredients", "ส่งต่อไปหน้าเมนู"))
     + box("check", "Checkpoint 7",
           ul("วิเคราะห์รูปจริงได้ และรายการที่ AI เห็นตรงกับของในรูปอย่างน้อย 70%",
              "ส่งต่อไปหน้าเมนูแล้วได้เมนูจากของในรูป (ถ่ายภาพหน้าจอ 3 ภาพ: รูป, ผลวิเคราะห์, เมนู)",
              "รูปที่ไม่ใช่อาหารไม่ทำให้แอป crash")),
     kind="ทำเอง")

# ================================================================ STEP 8
step(8, "ตรวจสอบรอบสุดท้าย แก้ปัญหา และสร้าง APK", 20,
     "เทสต์ผ่านครบ · ไม่มีคำเตือนจาก analyzer · ได้ไฟล์ APK ติดตั้งบนมือถือ",
     code("flutter analyze     # ต้อง No issues found\nflutter test        # ต้อง 12 passed", "bash")
     + p("ถ้าคุณใส่บรรทัด " + c("// ignore_for_file: ...") + " ที่ starter ให้มาไว้บนสุดของ 4 ไฟล์ ตอนนี้ลบออกได้แล้ว (มันมีไว้ปิดคำเตือนตอนโค้ดยังไม่ครบ)")
     + h3("8.1 ปัญหาที่พบบ่อย")
     + table(["อาการ", "สาเหตุ", "แก้"], [
         ["กดปุ่มแล้วไม่มีอะไรเกิดขึ้น / SnackBar \"ยังไม่ได้เขียน\"", "ยังไม่ได้ลบโค้ด TODO ใน starter", "ลบ SnackBar/throw UnimplementedError ออกให้หมด"],
         ["\"API key ไม่ถูกต้อง\" ทั้งที่วางถูก", "มีช่องว่าง/บรรทัดใหม่ติดมาตอน copy · key ถูกลบใน AI Studio", "พิมพ์ใหม่ · สร้าง key ใหม่"],
         ["429 บ่อย", "ทั้งห้องใช้ Wi-Fi เดียวกัน? ไม่เกี่ยว — โควตานับต่อ key · กดถี่เกินโควตาต่อนาที", "รอ 1 นาที · เปลี่ยน kGeminiModel เป็นรุ่น lite"],
         ["\"AI ตอบช้าเกินไป (เกิน 90 วินาที)\" / รอนานมาก", "โมเดล 3.x คิดนานเพราะ thinkingLevel สูง หรือ Google คนเยอะ", "ตรวจว่า body มี thinkingConfig (Step 5.2) · ลด kThinkingLevel เป็น low · เปลี่ยนเป็น gemini-3.5-flash-lite · ย่อรูปให้เล็กลง"],
         ["404 ไม่พบโมเดล", "Google ปลดระวางชื่อโมเดลนั้นแล้ว", "เปิด ai.google.dev/gemini-api/docs/models เลือกรุ่น Flash ปัจจุบัน แก้ ai_config.dart"],
         ["\"อ่านคำตอบของ AI ไม่ได้: FormatException\"", "AI ตอบ JSON ไม่ครบ (ถูกตัดที่ maxOutputTokens) หรือไม่ได้ส่ง schema", "เพิ่ม maxOutputTokens · ลดจำนวนเมนู · ตรวจว่าส่ง responseSchema"],
         ["หน้ารูป: 400 Invalid argument / Unsupported MIME", "mime_type ไม่ตรงกับไฟล์ (เช่น HEIC จาก iPhone)", "ตั้ง imageQuality ให้ image_picker แปลงเป็น JPEG หรือ map HEIC → image/heic"],
         ["Unhandled Exception: setState() called after dispose()", "ไม่ได้เช็ก mounted หลัง await", "เพิ่ม " + c("if (!mounted) return;") + " ก่อน setState ทุกจุดหลัง await"],
         ["ปุ่มทดสอบขึ้น SocketException บนอีมูเลเตอร์", "อีมูเลเตอร์ไม่มีเน็ต (DNS)", "Cold boot อีมูเลเตอร์ หรือตั้ง DNS 8.8.8.8 ในเครื่อง"],
         ["คำตอบเป็นภาษาอังกฤษ", "system instruction ไม่ถูกส่ง (body ไม่มี system_instruction)", "ตรวจ Step 5.2 และเทสต์ข้อแรก"],
     ])
     + h3("8.2 สร้าง APK")
     + code("flutter build apk --release\n# ได้ไฟล์ build/app/outputs/flutter-apk/app-release.apk (~20 MB)", "bash")
     + p("ส่งไฟล์ APK เข้ามือถือ (LINE/Drive/สาย USB) → เปิดไฟล์ → อนุญาตติดตั้งจากแหล่งที่ไม่รู้จัก → เปิดแอป → ใส่ key ที่หน้าตั้งค่า (key ไม่ได้ติดไปกับ APK — ดี เพราะถ้าแชร์ APK ให้เพื่อน เขาต้องใช้ key ของตัวเอง)")
     + box("check", "Checkpoint 8",
           ul("flutter analyze สะอาด · flutter test 12/12",
              "APK ติดตั้งและใช้งานบนมือถือจริงได้ทั้ง 2 ฟีเจอร์")))

# ================================================================ STEP 9
step(9, "โจทย์ท้าทาย (เลือกทำ) และสิ่งที่ต้องส่ง", 60,
     "ต่อยอดแอปด้วยตัวเองอย่างน้อย 1 ข้อ และส่งงานครบ",
     p("เลือกทำ<b>อย่างน้อย 1 ข้อ</b> (ข้อ A–B ง่าย · C–D ปานกลาง · E ยาก) ทุกข้อใช้ความรู้ที่มีอยู่แล้วในแล็บนี้ มีคำใบ้ให้ แต่ไม่มีเฉลย")
     + box("challenge", "A · เลือกจำนวนเมนู (ง่าย)",
           ul("เพิ่ม " + c("DropdownButton") + " หรือ " + c("SegmentedButton") + " ให้เลือก 3 / 5 / 8 เมนู ในหน้าวัตถุดิบ",
              "คำใบ้: เพิ่มพารามิเตอร์ " + c("count") + " ให้ " + c("buildMenuPrompt") + " และ " + c("suggestMenus") + " (อย่าลืมแก้ " + c("AiService") + " ทั้ง 2 implementation)"))
     + box("challenge", "B · ถามเชฟต่อ (ง่าย–ปานกลาง)",
           ul("ใต้การ์ดเมนู เพิ่มช่อง \"ถามเพิ่มเกี่ยวกับเมนูนี้\" เช่น \"ถ้าไม่มีซอสหอยนางรมใช้อะไรแทน\"",
              "คำใบ้: เพิ่มเมธอด " + c("ask(String question, {String? context})") + " ใน AiService ที่เรียก generate <b>โดยไม่ส่ง schema</b> (ได้ข้อความธรรมดา) และใส่ชื่อเมนู+วัตถุดิบลงใน prompt เป็นบริบท",
              "ขั้นสูง: ทำเป็นแชตต่อเนื่อง โดยส่ง " + c("contents") + " หลายรายการสลับ role " + c("user") + "/" + c("model") + " — ต้องแก้ " + c("generate()") + " ให้รับประวัติ"))
     + box("challenge", "C · บันทึกเมนูโปรด (ปานกลาง)",
           ul("ปุ่มหัวใจบน MenuCard → เก็บเมนูไว้ดูทีหลังโดยไม่ต้องถาม AI ใหม่ · หน้า \"เมนูโปรด\" บนหน้าแรก",
              "คำใบ้: เพิ่ม " + c("toJson()") + " ใน MenuSuggestion แล้วเก็บเป็น " + c("jsonEncode(list)") + " ใน shared_preferences (ดู app_settings.dart เป็นตัวอย่าง)"))
     + box("challenge", "D · แสดงค่าใช้จ่าย token (ปานกลาง)",
           ul("แสดงใต้ผลลัพธ์ว่า \"ใช้ไป 1,130 token\" จาก " + c("usageMetadata.totalTokenCount") + " ใน response",
              "คำใบ้: generate() ตอนนี้คืน String อย่างเดียว — เปลี่ยนให้คืนคลาสใหม่ " + c("GeminiReply {String text; int totalTokens;}") + " แล้วไล่แก้ที่เรียกใช้ (compiler จะบอกครบทุกจุด) · เทสต์เดิมต้องยังผ่าน"))
     + box("challenge", "E · สแกนใบเสร็จซูเปอร์ (ยาก)",
           ul("ถ่ายรูปใบเสร็จ → AI อ่านรายการสินค้า+ราคา → สรุปว่าซื้ออะไรมาบ้างและทำเมนูอะไรได้",
              "คำใบ้: ใช้ analyzePhoto โครงเดิม แต่เขียน prompt + schema ใหม่ (" + c("items[{name, price, qty}]") + ", " + c("total") + ") และหน้าจอใหม่ · ระวังรูปใบเสร็จต้องชัด ให้ maxWidth 1600"))
     + h3("สิ่งที่ต้องส่ง")
     + table(["รายการ", "รูปแบบ"], [
         ["1. ลิงก์ GitHub ของโปรเจกต์คุณ (repo ส่วนตัวที่ fork/คัดลอกไป)", "ต้องมี commit อย่างน้อย 3 ครั้ง (Step 5, 6, 7) และ <b>ไม่มี API key ในโค้ด</b> — ผู้สอนจะ grep หา \"AIza\""],
         ["2. ภาพหน้าจอ", "curl (Step 1) · ทดสอบการเชื่อมต่อ (Step 5) · เมนูจากวัตถุดิบ 2 ภาพ (Step 6) · รูป+ผลวิเคราะห์+เมนู 3 ภาพ (Step 7)"],
         ["3. บันทึกการทดลอง prompt", "ตาราง: แก้อะไร / คาดว่า / เห็นจริง อย่างน้อย 2 ข้อ (Step 6.5)"],
         ["4. โจทย์ท้าทาย", "บอกว่าทำข้อไหน + ภาพหน้าจอ + อธิบาย 3–5 บรรทัดว่าแก้ไฟล์ไหนบ้าง"],
         ["5. ตอบคำถามสั้น ๆ", "(ก) ทำไมแอปนี้ไม่ต้องมีเซิร์ฟเวอร์ PHP เหมือน LabStock แล้วถ้าจะทำแอปขายจริงควรมีไหม เพราะอะไร (ข) responseSchema ช่วยอะไร ถ้าไม่มีจะเกิดอะไร (ค) ถ้า Google เปลี่ยนชื่อโมเดล ต้องแก้กี่ไฟล์"],
     ])
     + box("warn", "เรื่อง key อีกครั้ง",
           ul("ก่อน push ขึ้น GitHub ให้ค้นหาคำว่า " + c("AIza") + " ทั้งโปรเจกต์ ต้องไม่เจอ",
              "ถ้าเผลอ push ไปแล้ว การลบ commit ไม่พอ (ประวัติยังอยู่) — ไปลบ key ใน AI Studio แล้วสร้างใหม่ทันที")),
     kind="ทำเอง")

# ================================================================ CSS + render
CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
* { box-sizing: border-box; }
html { font-size: 16pt; }
body { font-family: 'TH Sarabun New', 'TH SarabunPSK', 'Sarabun', sans-serif; font-size: 16pt; line-height: 1.35; color: #1a1a1a; margin: 0; }
h1, h2, h3 { color: #1b5e20; margin: 0.6em 0 0.3em; line-height: 1.2; }
h1 { font-size: 30pt; } h2 { font-size: 24pt; border-bottom: 2px solid #2e7d32; padding-bottom: 4px; margin-top: 1em; } h3 { font-size: 19pt; color: #2e7d32; }
p { margin: 0.35em 0 0.6em; } ul, ol { margin: 0.2em 0 0.7em; padding-left: 1.5em; } li { margin: 0.12em 0; }
code { font-family: Menlo, 'SF Mono', Consolas, monospace; font-size: 10.5pt; background: #eef4ee; padding: 1px 5px; border-radius: 4px; }
.codeblock { margin: 0.5em 0 0.9em; border: 1px solid #cfd8cf; border-radius: 6px; overflow: hidden; page-break-inside: avoid; }
.codecap { display: flex; justify-content: space-between; background: #2e7d32; color: #fff; font-family: Menlo, monospace; font-size: 10pt; padding: 4px 10px; }
.codecap .lines { opacity: 0.85; }
pre.hl { margin: 0; padding: 8px 10px; font-family: Menlo, 'SF Mono', Consolas, monospace; font-size: 9.6pt; line-height: 1.32; white-space: pre-wrap; word-break: break-all; background: #f6f9f6; }
pre.hl .gi { background: #dcf5dc; color: #0b5a0b; display: inline-block; width: 100%; } pre.hl .gd { background: #fde0e0; color: #8a0000; display: inline-block; width: 100%; }
pre.hl .gu { color: #6a1b9a; font-weight: bold; }
.box { border-left: 6px solid; border-radius: 6px; padding: 8px 14px 6px; margin: 0.8em 0; page-break-inside: avoid; }
.box .boxtitle { font-weight: bold; font-size: 17pt; margin-bottom: 2px; } .box ul, .box ol { margin-bottom: 0.3em; }
.box.learn { border-color: #03a9f4; background: #e8f6fd; } .box.learn .boxtitle { color: #01579b; }
.box.check { border-color: #2e7d32; background: #eaf5ea; } .box.check .boxtitle { color: #1b5e20; } .box.check .boxtitle::before { content: '✔ '; }
.box.challenge { border-color: #ffb300; background: #fff7e0; } .box.challenge .boxtitle { color: #8d5a00; }
.box.warn { border-color: #d32f2f; background: #fdecea; } .box.warn .boxtitle { color: #b71c1c; }
.box .codeblock { page-break-inside: auto; }
.step { page-break-before: always; }
.stephead { background: #2e7d32; color: #fff; padding: 12px 18px; border-radius: 8px; margin-bottom: 10px; }
.stephead.diy { background: #ef6c00; }
.stephead .no { font-size: 13pt; letter-spacing: 1px; opacity: 0.85; } .stephead h1 { color: #fff; margin: 0; font-size: 26pt; } .stephead .meta { font-size: 14pt; opacity: 0.9; margin-top: 4px; }
.goal { border: 1px dashed #2e7d32; padding: 6px 12px; border-radius: 6px; margin-bottom: 8px; } .goal b { color: #1b5e20; }
table.tbl { border-collapse: collapse; width: 100%; margin: 0.5em 0 1em; font-size: 14.5pt; }
table.tbl th, table.tbl td { border: 1px solid #c9d6c9; padding: 4px 8px; vertical-align: top; } table.tbl th { background: #e8f5e9; color: #1b5e20; text-align: left; }
table.tbl .codeblock { margin: 0.2em 0; }
.figrow { display: flex; gap: 8mm; justify-content: center; flex-wrap: wrap; margin: 0.6em 0 1em; page-break-inside: avoid; }
figure.shot { margin: 0; text-align: center; }
figure.shot img { width: 100%; border: 1px solid #c9ccd9; border-radius: 10px; }
figure.shot figcaption { font-size: 13pt; color: #444; margin-top: 3px; }
figure.shot .noshot { border: 1px dashed #aaa; padding: 30mm 4mm; color: #888; font-size: 12pt; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; }
.cover .band { background: #2e7d32; color: #fff; padding: 30px 36px; border-radius: 14px; }
.cover .band .sup { font-size: 16pt; opacity: 0.85; } .cover .band h1 { color: #fff; font-size: 40pt; margin: 4px 0; } .cover .band .sub { font-size: 22pt; }
.cover .info { margin-top: 26px; font-size: 17pt; line-height: 1.6; } .cover .accent { height: 8px; background: linear-gradient(90deg, #ff8f00, #03a9f4); border-radius: 4px; margin-top: 18px; }
.small { font-size: 13pt; color: #555; }
"""

H: list[str] = []
H.append("<!DOCTYPE html><html lang='th'><head><meta charset='utf-8'><title>KitchenAI คู่มือปฏิบัติการ</title>")
H.append("<style>" + CSS + FMT.get_style_defs(".hl") + "</style></head><body>")
H.append(f"""
<div class="cover">
  <div class="band">
    <div class="sup">คู่มือปฏิบัติการ · รายวิชา 5534408 การพัฒนาแอปพลิเคชันบนอุปกรณ์เคลื่อนที่</div>
    <h1>KitchenAI</h1>
    <div class="sub">สร้างแอป Flutter ที่คุยกับ AI (Gemini): แนะนำเมนูจากวัตถุดิบ และดูรูปแล้วบอกว่ามีอะไร</div>
  </div>
  <div class="accent"></div>
  <div class="info">
    <b>ฉบับนักศึกษา · เรียนรู้ด้วยตนเอง</b> · Step 1–9 · ใช้ของฟรีทั้งหมด (Flutter · Gemini API free tier · GitHub)<br>
    ใช้ Android Studio · ต่อยอดจากความรู้ http / JSON / shared_preferences / image_picker ที่เรียนจาก LabStock<br>
    <span class="small">โค้ด: {REPO} · tag {START_TAG} (เริ่มทำ) · {DONE_TAG} (เฉลย) · ปรับปรุง {TODAY_TH}</span>
  </div>
</div>
""")

# ---- ก่อนเริ่ม
H.append('<div class="step"><h2>ก่อนเริ่ม: แอปนี้ทำอะไร และคุณจะได้เรียนอะไร</h2>')
H.append(p("KitchenAI เป็นแอปมือถือเล็ก ๆ ที่ส่งคำถามไปให้ AI (Google Gemini) แล้วเอาคำตอบมาแสดงเป็นหน้าจอสวย ๆ มี 2 ฟีเจอร์:"))
H.append(table(["ฟีเจอร์", "ผู้ใช้ทำอะไร", "AI ทำอะไร", "เทคนิค"], [
    ["เมนูจากวัตถุดิบ", "พิมพ์ของที่มี เช่น ไข่ หมูสับ กระเทียม", "คิดเมนู 3 อย่าง บอกวัตถุดิบ ของที่ต้องซื้อเพิ่ม วิธีทำทีละขั้น", "HTTP POST · JSON · prompt · บังคับ AI ตอบเป็น JSON"],
    ["ถ่ายรูปวัตถุดิบ", "ถ่ายรูปของในตู้เย็น", "บอกว่าเห็นอะไร ปริมาณเท่าไร แล้วส่งต่อไปคิดเมนู", "image_picker · base64 · ส่งรูป+ข้อความพร้อมกัน (multimodal)"],
]))
H.append(fig(("04_home_demo", "หน้าแรก"), ("08_ingredients_result", "เมนูจากวัตถุดิบ"), ("12_photo_result", "ผลวิเคราะห์รูป"), width_mm=44))
H.append(h3("คำศัพท์ที่จะเจอตลอดเล่ม"))
H.append(table(["คำ", "ความหมายแบบบ้าน ๆ"], [
    ["LLM / โมเดล", "โปรแกรม AI ที่รับข้อความ (และรูป) แล้วเขียนข้อความตอบ เช่น Gemini, GPT, Claude — เราไม่ได้รันมันเอง แต่เรียกผ่านอินเทอร์เน็ต"],
    ["API", "ช่องทางให้โปรแกรมคุยกับโปรแกรม — ของ Gemini คือ URL ที่รับ JSON แล้วตอบ JSON เหมือน PHP API ใน LabStock"],
    ["API key", "รหัสประจำตัวที่แนบไปทุกคำขอ บอกว่าเป็นเรา และนับโควตาของเรา"],
    ["prompt", "ข้อความที่เราส่งไปถาม/สั่ง AI · <b>system instruction</b> = prompt พิเศษที่บอกบทบาทและกติกา ใช้กับทุกคำถาม"],
    ["token", "หน่วยนับความยาวข้อความที่ AI ใช้ (คำไทย 1 คำ ≈ 1–3 token) โควตาฟรีนับเป็น token และคำขอต่อนาที/วัน"],
    ["temperature", "ตัวเลข 0–2 ควบคุมความสุ่ม: ต่ำ = ตอบเหมือนเดิมทุกครั้ง · สูง = หลากหลาย/สร้างสรรค์"],
    ["JSON schema", "แบบฟอร์มบอกโครงสร้าง JSON ที่ต้องการ ส่งไปให้ AI กรอกให้ตรง จะได้แปลงเป็น object ใน Dart ได้"],
    ["multimodal", "ส่งได้มากกว่าข้อความ — แล็บนี้ส่งรูปภาพไปพร้อมคำถาม"],
    ["base64", "วิธีเขียนไฟล์ไบนารี (รูป) เป็นตัวอักษร เพื่อยัดลงใน JSON ได้"],
]))
H.append(h3("สิ่งที่ต้องมี"))
H.append(ul("Android Studio + Flutter 3.35 ขึ้นไป (เครื่องที่ใช้ทำ LabStock ใช้ได้เลย) ตรวจด้วย " + c("flutter doctor"),
            "บัญชี Google สำหรับขอ API key (Step 1) และอินเทอร์เน็ตตอนทดสอบกับ AI จริง",
            "อีมูเลเตอร์หรือมือถือ Android (มือถือจริงจะได้ลองถ่ายรูปจริง)",
            "<b>ไม่ต้องมี</b> XAMPP, บัตรเครดิต หรือเซิร์ฟเวอร์ใด ๆ — ทุกอย่างในแล็บนี้ฟรี"))
H.append(h3("ลำดับที่จะทำ"))
H.append(table(["Step", "ประเภท", "หัวข้อ", "ทำเสร็จแล้วจะได้อะไร", "นาที"],
               [[str(s_["no"]), s_["kind"], f"<b>{s_['title']}</b>", s_["goal"], str(s_["minutes"])] for s_ in STEPS]
               + [["", "", "<b>รวม</b>", "", f"<b>{sum(s_['minutes'] for s_ in STEPS)}</b>"]]))
H.append(h3("ลิงก์"))
H.append(table(["ต้องการ", "ลิงก์ / คำสั่ง"], [
    ["ขอ API key", "https://aistudio.google.com/apikey"],
    ["โค้ดเริ่มต้น (ZIP)", f"{REPO}/archive/refs/tags/{START_TAG}.zip"],
    ["ใน Android Studio", "Get from VCS → " + c(REPO + ".git") + " → Git → Branches → Tags → " + c(START_TAG) + " → Checkout"],
    ["ดูเฉลยเทียบกับ starter", f"{REPO}/compare/{START_TAG}...{DONE_TAG}"],
    ["เอกสาร Gemini API", "https://ai.google.dev/gemini-api/docs · รายชื่อโมเดล: /models · โควตา: https://aistudio.google.com/rate-limit"],
]))
H.append(box("warn", "กติกา",
             ul("Step 5–7 ต้องเขียนเอง ห้ามคัดลอกเฉลยทั้งก้อน — เฉลยเปิดให้ดู<b>หลัง</b>พยายามเองแล้ว และผู้สอนจะสุ่มถามให้อธิบายโค้ดบรรทัดต่อบรรทัด",
                "ติดเกิน 30 นาที ถามในกลุ่มพร้อมแนบ error และบอกว่าลองอะไรไปแล้ว",
                "<b>ห้ามให้ API key หลุดขึ้น GitHub หรือกลุ่มแชต</b> ไม่ว่ากรณีใด")))
H.append("</div>")

for s_ in STEPS:
    diy = "diy" if s_["kind"] == "ทำเอง" else ""
    H.append(f"""<div class="step">
<div class="stephead {diy}"><div class="no">STEP {s_['no']} · {s_['kind']}</div><h1>{s_['title']}</h1>
<div class="meta">เวลาโดยประมาณ {s_['minutes']} นาที</div></div>
<div class="goal"><b>เป้าหมาย:</b> {s_['goal']}</div>
{s_['body']}
</div>""")

# ---- ภาคผนวก
H.append('<div class="step"><h2>ภาคผนวก ก: ไฟล์เฉลยฉบับเต็ม (ดูหลังทำเองแล้ว)</h2>')
H.append(p("ไฟล์ที่เหลือ (models, widgets, settings, home) เหมือนกันทั้ง starter และ done เปิดดูได้ในโปรเจกต์"))
for rel in ["lib/data/gemini_client.dart", "lib/data/ai_service.dart", "lib/screens/ingredients_screen.dart", "lib/screens/photo_screen.dart"]:
    H.append(h3(rel))
    H.append(file_block(rel, DONE_TAG))
H.append("</div>")

H.append('<div class="step"><h2>ภาคผนวก ข: starter → done เปลี่ยนอะไรบ้าง (diff)</h2>')
for rel in ["lib/data/gemini_client.dart", "lib/data/ai_service.dart", "lib/screens/ingredients_screen.dart", "lib/screens/photo_screen.dart"]:
    H.append(diff_block(rel))
H.append("</div>")

H.append('<div class="step"><h2>ภาคผนวก ค: Interactions API (ของใหม่จาก Google) ต่างจากที่เราใช้อย่างไร</h2>')
H.append(p("ปลายปี 2026 Google เพิ่ม API ตัวใหม่ชื่อ <b>Interactions</b> (" + c("POST /v1beta/interactions") + ") ที่เขียนสั้นกว่าและจำบทสนทนาฝั่งเซิร์ฟเวอร์ได้ ส่วน " + c("generateContent") + " ที่เราใช้ Google ระบุว่ายัง <i>fully supported</i> และเป็นแบบที่เอกสาร/ตัวอย่างบนอินเทอร์เน็ตส่วนใหญ่ใช้ จึงเหมาะกับการเรียนรู้โครงสร้างพื้นฐานมากกว่า ถ้าอยากลองของใหม่ ลองเทียบดู:"))
H.append(code('''POST https://generativelanguage.googleapis.com/v1beta/interactions
x-goog-api-key: <key>
{
  "model": "gemini-3.8-flash",
  "input": [
    { "type": "text",  "text": "ดูรูปนี้แล้วบอกว่ามีอะไรบ้าง" },
    { "type": "image", "data": "<base64>", "mime_type": "image/jpeg" }
  ],
  "system_instruction": "คุณคือเชฟ...",
  "response_format": { "type": "text", "mime_type": "application/json", "schema": { ... } }
}''', "json"))
H.append(p("โจทย์เสริม: เขียน " + c("InteractionsClient") + " ที่มี " + c("generate()") + " หน้าตาเหมือน GeminiClient แต่ยิง endpoint นี้ แล้วสลับใช้ใน AppSettings — ถ้าออกแบบชั้น AiService ไว้ดี หน้าจอไม่ต้องแก้แม้แต่บรรทัดเดียว"))
H.append("</div>")

H.append("</body></html>")
OUT_HTML.write_text("".join(H), encoding="utf-8")
print("HTML:", OUT_HTML)

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={OUT_PDF_RAW}", OUT_HTML.as_uri()], check=True, capture_output=True)

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(TTFont("Sarabun", str(Path.home() / "Library/Fonts/THSarabunNew.ttf")))
reader = PdfReader(str(OUT_PDF_RAW))
writer = PdfWriter()
total = len(reader.pages)
for i, page in enumerate(reader.pages):
    if i > 0:
        buf = BytesIO()
        cv = canvas.Canvas(buf, pagesize=A4)
        cv.setFont("Sarabun", 12)
        cv.setFillColorRGB(0.35, 0.35, 0.35)
        cv.drawString(16 * 72 / 25.4, 9 * 72 / 25.4, "KitchenAI · คู่มือปฏิบัติการ 5534408")
        cv.drawRightString(A4[0] - 16 * 72 / 25.4, 9 * 72 / 25.4, f"หน้า {i + 1} / {total}")
        cv.save()
        buf.seek(0)
        page.merge_page(PdfReader(buf).pages[0])
    writer.add_page(page)
writer.add_metadata({"/Title": "KitchenAI — แอป Flutter ที่คุยกับ AI", "/Author": "รายวิชา 5534408"})
with open(OUT_PDF, "wb") as f:
    writer.write(f)
OUT_PDF_RAW.unlink()
print(f"PDF: {OUT_PDF} ({total} pages)")
