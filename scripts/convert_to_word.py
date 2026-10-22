#!/usr/bin/env python3
"""
Markdown → Word 一键转换器
智能识别文档类型，针对 教案/课程总结/作业/板书分析 应用不同排版。
用法: python convert_to_word.py <目标文件夹>
"""

import sys, os, re, io
from pathlib import Path
from datetime import date

# ── Windows UTF-8 编码兼容 ──────────────────────────────────
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# ── 依赖检查 ──────────────────────────────────────────────
try:
    from docx import Document
    from docx.shared import Pt, Inches, Cm, RGBColor, Emu
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
    from docx.enum.style import WD_STYLE_TYPE
    from docx.oxml.ns import qn, nsdecls
    from docx.oxml import parse_xml
except ImportError:
    print("请先安装依赖：pip install python-docx pyyaml")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("请先安装依赖：pip install pyyaml")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════
# 颜色与字体常量
# ═══════════════════════════════════════════════════════════

DARK_BLUE   = RGBColor(0x1A, 0x3C, 0x6E)   # 标题/大标题
MID_BLUE    = RGBColor(0x2B, 0x57, 0x9A)   # H2
ACCENT_BLUE = RGBColor(0x3D, 0x7A, 0xBF)   # H3
LIGHT_BLUE  = RGBColor(0xD6, 0xE4, 0xF0)   # 表头背景
CODE_GRAY   = RGBColor(0xF2, 0xF2, 0xF2)   # 代码块背景
BORDER_GRAY = RGBColor(0xCC, 0xCC, 0xCC)   # 表格/代码边框
DARK_GRAY   = RGBColor(0x33, 0x33, 0x33)   # 正文
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
RED_ACCENT  = RGBColor(0xC0, 0x39, 0x2B)
GREEN_OK    = RGBColor(0x27, 0xAE, 0x60)

FONT_BODY   = "Microsoft YaHei"
FONT_CODE   = "Consolas"
FONT_HEADING = "Microsoft YaHei"


# ═══════════════════════════════════════════════════════════
# Markdown 解析器
# ═══════════════════════════════════════════════════════════

class MDBlock:
    """一个 Markdown 块"""
    def __init__(self, kind, text="", meta=None):
        self.kind = kind          # h1/h2/h3/h4/table/code/list/hr/inline
        self.text = text          # 内容
        self.meta = meta or {}    # 额外信息（如表格行列）
        self.level = 0            # heading level


def parse_markdown(text):
    """将 Markdown 文本解析为块列表和 frontmatter"""
    lines = text.split("\n")
    blocks = []
    frontmatter = {}
    max_iter = len(lines) * 200 + 2000  # 安全上限

    # 解析 YAML frontmatter
    if lines and lines[0].strip() == "---":
        fm_lines = []
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            fm_lines.append(lines[i])
            i += 1
        if i < len(lines) and lines[i].strip() == "---":
            try:
                frontmatter = yaml.safe_load("\n".join(fm_lines)) or {}
            except Exception:
                pass
            lines = lines[i+1:]
        else:
            lines = lines[1:]

    n = len(lines)
    i = 0
    _iter = 0
    while i < n and _iter < max_iter:
        _iter += 1
        line = lines[i]

        # 空行
        if not line.strip():
            i += 1
            continue

        # 代码块
        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
                _iter += 1
            i += 1
            blocks.append(MDBlock("code", "\n".join(code_lines)))
            continue

        # 表格
        if "|" in line and i + 1 < n and re.match(r'^[\|\s\-:]+$', lines[i+1].strip()):
            header = [c.strip() for c in line.strip().split("|") if c.strip()]
            i += 2
            rows = [header]
            while i < n and "|" in lines[i]:
                row = [c.strip() for c in lines[i].strip().split("|") if c.strip()]
                if row:
                    rows.append(row)
                i += 1
                _iter += 1
            blocks.append(MDBlock("table", meta={"rows": rows}))
            continue

        # 标题
        h_match = re.match(r'^(#{1,6})\s+(.+)', line)
        if h_match:
            level = len(h_match.group(1))
            blocks.append(MDBlock(f"h{level}", h_match.group(2), meta={"level": level}))
            i += 1
            continue

        # 水平线
        if re.match(r'^[-\*_]{3,}\s*$', line.strip()):
            blocks.append(MDBlock("hr"))
            i += 1
            continue

        # 有序列表
        if re.match(r'^(\d+\.)\s+(.+)', line):
            items = []
            while i < n and re.match(r'^(\d+\.)\s+(.+)', lines[i]):
                m = re.match(r'^(\d+\.)\s+(.+)', lines[i])
                if m:
                    items.append(m.group(2))
                i += 1
                _iter += 1
            blocks.append(MDBlock("ordered_list", meta={"items": items}))
            continue

        # 无序列表
        if re.match(r'^[\-\*\+]\s+(.+)', line):
            items = []
            while i < n and re.match(r'^[\-\*\+]\s+(.+)', lines[i]):
                m = re.match(r'^[\-\*\+]\s+(.+)', lines[i])
                if m:
                    items.append(m.group(1))
                i += 1
                _iter += 1
            blocks.append(MDBlock("unordered_list", meta={"items": items}))
            continue

        # 普通段落（含行内 | 但非表格的兜底处理）
        para_lines = []
        while i < n and lines[i].strip() and \
              not re.match(r'^(#{1,6})\s+', lines[i]) and \
              not re.match(r'^[\-\*\+]\s+', lines[i]) and \
              not re.match(r'^(\d+\.)\s+', lines[i]) and \
              not lines[i].strip().startswith("```") and \
              "|" not in lines[i]:
            para_lines.append(lines[i])
            i += 1
            _iter += 1
        if para_lines:
            blocks.append(MDBlock("paragraph", "\n".join(para_lines)))
        else:
            # 当前行未被任何块类型匹配（如含 | 但无表格分隔行），跳过避免死循环
            i += 1

    if _iter >= max_iter:
        print(f"  [WARN] Parser hit max iterations, output may be partial")

    return frontmatter, blocks


def detect_doc_type(frontmatter, blocks):
    """识别文档类型：lesson_plan / lesson_summary / homework / board_teaching / board_summary"""
    # 从 frontmatter
    lt = (frontmatter.get("lesson_type") or "").lower()
    if "模块同步" in lt or "mixed" in lt:
        return "lesson_plan"
    if lt == "board":
        return "board_teaching"

    # 从 H1 标题
    for b in blocks:
        if b.kind == "h1":
            t = b.text.lower()
            if "lesson plan" in t or "教案" in t:
                return "lesson_plan"
            if "homework" in t or "作业" in t:
                return "homework"
            if "板书" in t:
                return "board_teaching"
            if "board" in t and "summary" in t:
                return "board_summary"
            if "lesson summary" in t or "教学总结" in t or "总结" in t:
                return "lesson_summary"
            break

    # 从内容特征
    text_body = " ".join(b.text for b in blocks if b.text)
    if "上堂回顾" in text_body or "今日词汇" in text_body or "今日句式" in text_body or "随堂练习" in text_body:
        return "board_teaching"
    if "homework" in text_body.lower() or "vocabulary practice" in text_body.lower():
        return "homework"
    if "grammar detected" in text_body.lower():
        return "board_summary"
    if "lesson topic" in text_body.lower() and "grammar points" in text_body.lower():
        return "lesson_summary"

    return "lesson_plan"  # 默认


# ═══════════════════════════════════════════════════════════
# Word 生成器 — 样式工厂
# ═══════════════════════════════════════════════════════════

class WordBuilder:
    def __init__(self, doc_type):
        self.doc = Document()
        self.doc_type = doc_type

        # 页面设置
        section = self.doc.sections[0]
        section.page_width  = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

        # 样式
        style = self.doc.styles['Normal']
        style.font.name = FONT_BODY
        style.font.size = Pt(11)
        style.font.color.rgb = DARK_GRAY
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.line_spacing = 1.25
        # 设置中文字体
        rPr = style.element.get_or_add_rPr()
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="{FONT_BODY}"/>')
        rPr.append(rFonts)

        self._setup_styles()

    def _setup_styles(self):
        """预设自定义样式；board_teaching 用大字排版"""
        is_board = (self.doc_type == "board_teaching")

        # Heading 1
        h1 = self.doc.styles['Heading 1']
        h1.font.name = FONT_HEADING
        h1.font.size = Pt(26) if is_board else Pt(22)
        h1.font.bold = True
        h1.font.color.rgb = DARK_BLUE
        h1.paragraph_format.space_before = Pt(24) if is_board else Pt(18)
        h1.paragraph_format.space_after = Pt(16) if is_board else Pt(12)
        if is_board:
            h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Heading 2
        h2 = self.doc.styles['Heading 2']
        h2.font.name = FONT_HEADING
        h2.font.size = Pt(20) if is_board else Pt(16)
        h2.font.bold = True
        h2.font.color.rgb = MID_BLUE
        h2.paragraph_format.space_before = Pt(20) if is_board else Pt(14)
        h2.paragraph_format.space_after = Pt(12) if is_board else Pt(8)

        # Heading 3
        h3 = self.doc.styles['Heading 3']
        h3.font.name = FONT_HEADING
        h3.font.size = Pt(16) if is_board else Pt(13)
        h3.font.bold = True
        h3.font.color.rgb = ACCENT_BLUE
        h3.paragraph_format.space_before = Pt(14) if is_board else Pt(10)
        h3.paragraph_format.space_after = Pt(8) if is_board else Pt(6)

        # Heading 4
        h4 = self.doc.styles['Heading 4']
        h4.font.name = FONT_HEADING
        h4.font.size = Pt(14) if is_board else Pt(11.5)
        h4.font.bold = True
        h4.font.color.rgb = DARK_GRAY
        h4.paragraph_format.space_before = Pt(10) if is_board else Pt(8)
        h4.paragraph_format.space_after = Pt(6) if is_board else Pt(4)

        # Normal (body)
        if is_board:
            style = self.doc.styles['Normal']
            style.font.size = Pt(14)
            style.paragraph_format.line_spacing = 1.6

        # Store flag for later use
        self._is_board = is_board

    def add_meta_header(self, frontmatter):
        """在文档顶部添加元信息（仅 lesson_summary 和 homework）"""
        if not frontmatter:
            return

        meta_items = []
        for k in ["student_id", "student_ids", "student_name", "student_names",
                   "lesson_id", "date", "lesson_type", "duration", "difficulty"]:
            v = frontmatter.get(k)
            if v:
                if isinstance(v, list):
                    v = ", ".join(str(x) for x in v)
                label = {"student_id": "Student ID", "student_ids": "Student IDs",
                         "student_name": "Student", "student_names": "Students",
                         "lesson_id": "Lesson ID", "date": "Date",
                         "lesson_type": "Type", "duration": "Duration",
                         "difficulty": "Difficulty"}.get(k, k)
                meta_items.append((label, str(v)))

        if not meta_items:
            return

        # 创建信息表
        table = self.doc.add_table(rows=len(meta_items), cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        table.style = 'Light Grid Accent 1'

        for idx, (label, value) in enumerate(meta_items):
            c0 = table.cell(idx, 0)
            c1 = table.cell(idx, 1)
            p0 = c0.paragraphs[0]; p0.clear(); self._apply_inline_formatting(p0, label)
            p1 = c1.paragraphs[0]; p1.clear(); self._apply_inline_formatting(p1, value)
            for run in p0.runs:
                run.bold = True
                run.font.size = Pt(9)
                self._set_run_cjk_font(run, FONT_BODY)
            for run in p1.runs:
                run.font.size = Pt(9)
                self._set_run_cjk_font(run, FONT_BODY)

        # 设置第一列宽度
        for row in table.rows:
            row.cells[0].width = Cm(3.5)

        self.doc.add_paragraph("")  # spacing

    def add_block(self, block):
        """添加一个 Markdown 块到文档"""
        if block.kind in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._add_heading(block)
        elif block.kind == "paragraph":
            self._add_paragraph(block.text)
        elif block.kind == "table":
            self._add_table(block.meta.get("rows", []))
        elif block.kind == "code":
            self._add_code_block(block.text)
        elif block.kind == "unordered_list":
            self._add_list(block.meta.get("items", []), ordered=False)
        elif block.kind == "ordered_list":
            self._add_list(block.meta.get("items", []), ordered=True)
        elif block.kind == "hr":
            self._add_hr()

    def _add_heading(self, block):
        level = block.level
        text = block.text
        if level == 1:
            p = self.doc.add_heading(text, level=1)
        elif level == 2:
            p = self.doc.add_heading(text, level=2)
        elif level == 3:
            p = self.doc.add_heading(text, level=3)
        else:
            p = self.doc.add_heading(text, level=4)

    def _add_paragraph(self, text):
        """添加带内联格式的段落"""
        p = self.doc.add_paragraph()
        self._apply_inline_formatting(p, text)

    def _add_list(self, items, ordered=False):
        """添加列表"""
        for idx, item in enumerate(items):
            prefix = f"{idx+1}. " if ordered else "• "
            p = self.doc.add_paragraph(style='List Bullet' if not ordered else 'List Number')
            # Clear default text and add formatted
            p.clear()
            self._apply_inline_formatting(p, item)
            p.paragraph_format.left_indent = Cm(1)
            p.paragraph_format.first_line_indent = Cm(-0.5)

    def _add_table(self, rows):
        """添加格式化表格"""
        if not rows:
            return

        num_cols = max(len(r) for r in rows)
        num_rows = len(rows)
        table = self.doc.add_table(rows=num_rows, cols=num_cols)
        table.style = 'Light Grid Accent 1'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        for i, row_data in enumerate(rows):
            for j, cell_text in enumerate(row_data):
                if j < num_cols:
                    cell = table.cell(i, j)
                    p = cell.paragraphs[0]
                    p.clear()
                    self._apply_inline_formatting(p, cell_text)
                    p.paragraph_format.space_before = Pt(3)
                    p.paragraph_format.space_after = Pt(3)
                    for run in p.runs:
                        run.font.size = Pt(12) if self._is_board else Pt(9.5)
                        self._set_run_cjk_font(run, FONT_BODY)
                        if i == 0:
                            run.bold = True
                            run.font.color.rgb = WHITE
                    if i == 0:
                        shading = parse_xml(
                            f'<w:shd {nsdecls("w")} w:fill="1A3C6E" w:val="clear"/>'
                        )
                        cell._tc.get_or_add_tcPr().append(shading)

        self.doc.add_paragraph("")

    def _add_code_block(self, text):
        """添加代码/对话块；board_teaching 用大号字体"""
        font_size = Pt(12) if self._is_board else Pt(9.5)
        for line in text.split("\n"):
            p = self.doc.add_paragraph()
            run = p.add_run(line)
            self._set_run_cjk_font(run, FONT_CODE)
            run.font.size = font_size
            run.font.color.rgb = RGBColor(0x2D, 0x2D, 0x2D)
            p.paragraph_format.space_before = Pt(2) if self._is_board else Pt(1)
            p.paragraph_format.space_after = Pt(2) if self._is_board else Pt(1)
            p.paragraph_format.left_indent = Cm(0.8)
            # 灰底
            shading = parse_xml(
                f'<w:shd {nsdecls("w")} w:fill="F2F2F2" w:val="clear"/>'
            )
            p.paragraph_format.element.get_or_add_pPr().append(shading)

        self.doc.add_paragraph("")

    def _add_hr(self):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        # 添加底部边框作为分隔线
        pPr = p._p.get_or_add_pPr()
        pBdr = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            f'<w:bottom w:val="single" w:sz="6" w:space="1" w:color="CCCCCC"/>'
            f'</w:pBdr>'
        )
        pPr.append(pBdr)

    def _set_run_cjk_font(self, run, font_name):
        """设置 run 的 ASCII 和东亚字体，防止中文乱码"""
        run.font.name = font_name
        rPr = run._r.get_or_add_rPr()
        rFonts = rPr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = parse_xml(f'<w:rFonts {nsdecls("w")}/>')
            rPr.append(rFonts)
        rFonts.set(qn('w:eastAsia'), font_name)

    def _apply_inline_formatting(self, paragraph, text):
        """解析内联格式：**粗体** *斜体* `代码` [链接](url)"""
        # 正则匹配内联片段
        pattern = re.compile(
            r'(\*\*(.+?)\*\*)|'        # **bold**
            r'(\*(.+?)\*)|'             # *italic*
            r'(`(.+?)`)|'               # `code`
            r'(\[(.+?)\]\((.+?)\))'     # [link](url)
        )

        last_end = 0
        for m in pattern.finditer(text):
            # 前置普通文本
            if m.start() > last_end:
                run = paragraph.add_run(text[last_end:m.start()])
                self._set_run_cjk_font(run, FONT_BODY)
                run.font.size = Pt(11)

            if m.group(2):  # **bold**
                run = paragraph.add_run(m.group(2))
                run.bold = True
                self._set_run_cjk_font(run, FONT_BODY)
                run.font.size = Pt(11)
            elif m.group(4):  # *italic*
                run = paragraph.add_run(m.group(4))
                run.italic = True
                self._set_run_cjk_font(run, FONT_BODY)
                run.font.size = Pt(11)
            elif m.group(6):  # `code`
                run = paragraph.add_run(m.group(6))
                self._set_run_cjk_font(run, FONT_CODE)
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(0xC0, 0x39, 0x2B)
            elif m.group(8):  # [link](url)
                run = paragraph.add_run(m.group(8))
                run.font.color.rgb = ACCENT_BLUE
                run.underline = True
                self._set_run_cjk_font(run, FONT_BODY)
                run.font.size = Pt(11)

            last_end = m.end()

        # 末尾剩余文本
        if last_end < len(text):
            run = paragraph.add_run(text[last_end:])
            self._set_run_cjk_font(run, FONT_BODY)
            run.font.size = Pt(11)

    def save(self, path):
        self.doc.save(str(path))


# ═══════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════

def convert_file(md_path):
    """转换单个 .md 文件为 .docx"""
    md_path = Path(md_path)
    if not md_path.exists():
        print(f"  ⚠ 文件不存在: {md_path}")
        return False

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter, blocks = parse_markdown(content)
    doc_type = detect_doc_type(frontmatter, blocks)

    type_labels = {
        "lesson_plan":    "教案",
        "lesson_summary": "课程总结",
        "homework":       "作业",
        "board_teaching": "板书",
        "board_summary":  "板书分析",
    }
    label = type_labels.get(doc_type, "文档")

    builder = WordBuilder(doc_type)

    # 文档类型标识徽章（顶部居中）
    badge = builder.doc.add_paragraph()
    badge.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = badge.add_run(f"📋 {label}")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run.italic = True

    builder.add_meta_header(frontmatter)

    for block in blocks:
        builder.add_block(block)

    # 输出路径
    out_path = md_path.with_suffix(".docx")
    builder.save(out_path)
    print(f"  ✅ {md_path.name} → {out_path.name}  [{label}]")
    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python convert_to_word.py <文件夹路径>")
        print("示例: python convert_to_word.py students/STU001/lessons")
        sys.exit(1)

    target_dir = Path(sys.argv[1]).resolve()
    if not target_dir.is_dir():
        print(f"❌ 目录不存在: {target_dir}")
        sys.exit(1)

    md_files = sorted(target_dir.glob("*.md"))
    if not md_files:
        print(f"[OK] {target_dir.name} 中没有 .md 文件，跳过。")
        return

    print(f"\n{'='*60}")
    print(f"📂 {target_dir}")
    print(f"   找到 {len(md_files)} 个 Markdown 文件")
    print(f"{'='*60}")

    success = 0
    for f in md_files:
        if convert_file(f):
            success += 1

    print(f"{'='*60}")
    print(f"✨ 完成: {success}/{len(md_files)} 个文件已转换为 Word 文档")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
