---
name: podcast-transcription-analysis
description: Transcribe podcasts via Whisper ASR and produce structured analysis notes with timestamped TOC. Handles xiaoyuzhoufm, ximalaya, YouTube, and direct audio sources.
category: media
---

# Podcast Transcription & Analysis Skill

## When to Use
- User provides a podcast episode (link or audio file) and wants structured "播客分析" notes
- User wants to extract key timestamps and produce a well-structured analysis document
- Two workflows: **合并版**（timestamps + existing rewritten text）and **完整版**（full transcribe + rewrite + timestamps）

## 两种工作流

### 合并版（用户已有改写稿）
适用于：用户已有改写好的播客分析文本，只需要加上时间戳目录
1. 从 transcript 提取关键时间戳
2. 将时间戳目录 + 改写稿正文合并成一个 docx（TOC 在前，正文在后）

### 完整版（从零开始）
适用于：用户只有音频链接，没有转写稿
1. 下载音频 → Whisper 转写 → 读取分析转写稿 → 改写正文 → 生成时间戳目录 → 合并 docx

---

## 完整版 Step-by-Step

### Step 1: 提取音频链接

**小宇宙 (xiaoyuzhoufm.com):**
```bash
curl -s "PODCAST_URL" -H "User-Agent: Mozilla/5.0" | grep -oE 'https?://[^\"]+\.(m4a|mp3|ogg)[^\"]*'
```
或通过浏览器 Console：
```javascript
JSON.stringify(window.__INITIAL_STATE__ || document.querySelector('audio')?.src)
```

**喜马拉雅直接链接：** 直接从页面 audio 标签或 JavaScript 状态中找 `jt.ximalaya.com` 域名的 URL。

**YouTube:** 用 youtube-content skill 获取 transcript。

**RSS feeds:** 从 RSS XML 中提取 enclosure URL。

### Step 2: 下载音频
```bash
curl -L -o podcast_audio.m4a "AUDIO_URL" --progress-bar
```

### Step 3: Whisper 转写
```bash
pip3 install openai-whisper
python3 -c "
import whisper
model = whisper.load_model('base')
result = model.transcribe('podcast_audio.m4a', language='zh', task='transcribe')
with open('transcript.txt', 'w') as f:
    for seg in result['segments']:
        start = seg['start']
        text = seg['text'].strip()
        if text:
            mins = int(start // 60)
            secs = int(start % 60)
            f.write(f'[{mins:02d}:{secs:02d}] {text}\n')
print('Done! Segments:', len(result['segments']))
"
```

### Step 4: 读取分析转写稿
```bash
wc -l transcript.txt
head -100 transcript.txt
grep -n "41:3[0-9]" transcript.txt
sed -n '1630,1750p' transcript.txt
```

### Step 5: 改写正文内容

**⚠️ 必须先阅读参考范本！**
改写前，先用 `read_file` 读取以下文件，理解优质播客分析的结构和文风：
`/Users/oliviavivas/.hermes/cache/documents/播客分析_合并版.docx`（Nicky/Museon AI 那期）

这期是质量标杆，必须严格参照它的结构：
- 顶部有 **一句话总结**（一个段落概括全期精华）
- 正文用 **H1 + H2 多级标题**（不是三个大Part平铺）
- 结尾有 **"谁适合听这期"** 和 **"怎么听最高效"**
- 时间戳标注在正文各段开头（斜体灰色）

**风格指南（核心原则，必须遵守）：**
- **一针见血**：直白、口语化，不冗长重复。不说"其实"、"基本上"、"这个事儿"。
- **推理链条**：每个观点都要有"因为…所以…"、"这意味着什么"，不止是结论，要写出为什么成立。不写描述性废话。
- **前因后果**：先铺垫背景，再说洞察，最后给结论。
- **信息差/核心观点不可精简**：有独到见解、反直觉的内容要保留原文的冲击力，原话细节要写进去。
- **有依据**：忠实于原话，不自己编推理。原话里有的数字、案例、名称都要保留。
- **口语化**：像给聪明朋友口述一样，不写学术报告。不写"可以看出"、"表明了"、"体现了"。
- **H2标题本身即观点**：H2标题不是描述性词语，而是这一段的核心观点结论。

### Step 6: 生成时间戳目录

从转写稿中提取关键时间节点，格式：
```
{HH:MM}  {精准详细的小标题}
```

**小标题命名规则（来自 PingCAP 播客示例）：**
- ✅ `00:49  嘉宾背景介绍——对外经贸毕业、产品经理、连续创业者，Museon AI天使轮融资`
- ❌ `00:49  嘉宾背景`
- 要写出"这个时间点在讲什么 + 有什么关键细节"，让读者不看正文也能知道大概内容

**时间戳去重**：同一时间点出现在多个 Part 里，只保留第一次出现的条目

### Step 7: 生成 DOCX 文件

**⚠️ 重要：不要用 heredoc 写法写含中文引号的 Python 脚本！**
中文/英文的 fancy quotes（`""`、`''`、`""`）在 heredoc 里会导致 `SyntaxError: invalid syntax`。
正确做法：**始终把 Python 脚本写到 `/tmp/script.py` 再运行**。

使用 `/Applications/Xcode.app/Contents/Developer/usr/bin/python3`（execute_code 里的 Python 没有 python-docx）：

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn


doc = Document()

# 设置中文字体
style = doc.styles['Normal']
style.font.name = 'Microsoft YaHei'
style.font.size = Pt(11)
style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

# 标题
title = doc.add_heading('播客分析标题', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 副标题
sub = doc.add_paragraph('播客信息副标题')
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph('')

# ===== 时间戳目录 =====
doc.add_heading('时间戳目录', level=1)

timestamps = [
    ("00:49", "嘉宾背景介绍——对外经贸毕业、产品经理、连续创业者，Museon AI天使轮融资"),
    ("02:07", "在夜店拉老外教中文——非标准场景里的商业机会"),
    # ...更多时间戳
]

for ts, desc in timestamps:
    p = doc.add_paragraph()
    r1 = p.add_run(f"{ts}  ")
    r1.bold = True
    r1.font.size = Pt(11)
    r2 = p.add_run(desc)
    r2.font.size = Pt(11)
    p.paragraph_format.space_after = Pt(3)

doc.add_page_break()

# ===== 正文各章节 =====
# 每个章节 = doc.add_heading(H1, level=1) + 若干 doc.add_heading(H2, level=2) + 正文段落

# 示例结构：
doc.add_heading('一句话总结', level=1)
doc.add_paragraph('这一期最核心的观点，一段话概括全文精华...')

doc.add_heading('嘉宾背景：从X到Y', level=1)
doc.add_heading('XXX是谁 [HH:MM]', level=2)
doc.add_paragraph('正文段落...')
doc.add_heading('为什么这段经历重要 [HH:MM]', level=2)
doc.add_paragraph('正文段落...')

doc.add_heading('核心洞察：XXX', level=1)
doc.add_heading('第一个洞察点 [HH:MM]', level=2)
doc.add_paragraph('正文段落，有推理链条...')
doc.add_heading('第二个洞察点 [HH:MM]', level=2)
doc.add_paragraph('正文段落，有推理链条...')

# ...以此类推

doc.add_heading('谁适合听这期', level=1)
doc.add_paragraph('1. 受众描述...')
doc.add_paragraph('2. 受众描述...')

doc.add_heading('怎么听最高效', level=1)
doc.add_paragraph('只关注XXX：从MM:SS听到MM:SS...')
doc.add_paragraph('想完整理解：从头听到尾...')

doc.save('/path/to/output.docx')
```

---

## 合并版 Step-by-Step

（用户已有改写稿，只需要加时间戳目录）

### Step 1: 读取改写稿
用 `execute_code` 读取现有 docx 文件的段落内容，观察其章节结构和标题层级。

### Step 2: 读取转写稿提取时间戳
从 transcript.txt 提取关键时间节点（如果本地没有转写稿，需要重新转写或从用户提供的其他资料获取）。

### Step 3: 生成合并版 DOCX
将时间戳目录 + 改写稿正文合并成一个 docx：
- 时间戳目录在最前面
- `doc.add_page_break()` 分隔
- 改写稿原文原版内容在后面（不改写，不调整内容）
- 注意：合并版的正文内容是用户已有的成熟改写稿，不做任何改动

---

## DOCX 结构规范

**文件命名**：`播客分析_合并版.docx` 或 `播客分析_最终版_含目录.docx`

**页面结构：**
1. 标题（居中，Heading 0）
2. 副标题信息（居中，普通段落）
3. 空行
4. 时间戳目录（Heading 1 + 44条时间戳条目）
5. `doc.add_page_break()`
6. 正文各章节

**时间戳目录格式：**
- 时间戳加粗：`r1.bold = True`
- 小标题不加粗，正文大小
- 段落后间距 Pt(3)
- 格式：`HH:MM  小标题——副标题/细节`

**正文格式：**
- 主要章节 Heading 1
- 分隔线 `——` 前后各留 Pt(6) 间距
- 时间戳行：斜体 + 灰色 (`RGBColor(0x60, 0x60, 0x60)`)
- **H2 标题后加时间戳**：所有 H2 标题在末尾加上对应内容的时间戳，格式为 ` [HH:MM]`，例如 `中型企业的处境——没人喜欢他们 [02:49]`

---

## Telegram 发送注意事项

```python
send_message(
    action="send",
    target="telegram:CHAT_ID",
    message="MEDIA:/path/to/file.docx"
)
```

**Telegram 发送 .docx 超时问题**：
- Telegram 发送大文件（.docx、音频等）经常超时，这是常见现象
- **不要用 MEDIA:路径 在文字消息里**，容易触发超时
- 正确方式：分两条发，先发纯文字说明文件路径，再发 MEDIA:文件路径
- 如果还是超时，重试1-2次往往能成功
- 实在不行就只发文字 + 文件路径，让用户手动打开

---

## 技术注意事项

1. **小宇宙音频链接在 JavaScript 状态里**：不在 HTML 里，直接 curl 抓不到。用浏览器 Console 找 `jt.ximalaya.com` 域名。
2. **Whisper 用 base 模型跑 CPU**：89分钟音频约3分钟转写完成。
3. **python-docx 路径**：必须用 `/Applications/Xcode.app/Contents/Developer/usr/bin/python3`，execute_code 的沙盒 Python 没有这个库。
4. **转写稿行数**：89分钟约 3000+ 行，用 `sed -n 'N,Np'` 分段读取，不要试图全量读入分析。
5. **音频 URL**：小宇宙是 `jt.ximalaya.com` 开头，喜马拉雅直接链接一般是 `aod.cos.tx.xmcdn.com`。
