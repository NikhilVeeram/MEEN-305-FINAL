import html
import re
import sys
from pathlib import Path


def clean_inline(text: str) -> str:
    text = text.replace("~", " ")
    text = text.replace("\\%", "%").replace("\\&", "&").replace("\\_", "_")
    text = text.replace("\\textbf{", "").replace("\\textit{", "")
    text = re.sub(r"\\url\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\ref\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    text = re.sub(r"\\caption\*?\{", "Caption: ", text)
    text = text.replace("\\mathrm{", "").replace("\\emph{", "")
    text = text.replace("\\circ", "deg")
    text = text.replace("\\approx", "approx.")
    text = text.replace("\\times", "x")
    text = text.replace("\\le", "<=").replace("\\ge", ">=")
    text = text.replace("\\pm", "+/-")
    text = text.replace("\\textwidth", "100%")
    text = re.sub(r"\$([^$]*)\$", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})", r"\1", text)
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def table_to_html(lines):
    rows = []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("\\") or line in {"\\toprule", "\\midrule", "\\bottomrule"}:
            continue
        line = line.rstrip("\\").strip()
        if "&" not in line:
            continue
        cells = [clean_inline(part.strip()) for part in line.split("&")]
        rows.append(cells)
    if not rows:
        return ""
    out = ["<table>"]
    for idx, row in enumerate(rows):
        tag = "th" if idx == 0 else "td"
        out.append("<tr>" + "".join(f"<{tag}>{html.escape(cell)}</{tag}>" for cell in row) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def convert(tex_path: Path, html_path: Path):
    text = tex_path.read_text(encoding="utf-8", errors="replace")
    text = text.split("\\begin{document}", 1)[-1]
    text = text.split("\\end{document}", 1)[0]
    lines = text.splitlines()

    body = []
    para = []
    in_table = False
    table_lines = []
    in_itemize = False

    def flush_para():
        if para:
            value = clean_inline(" ".join(para))
            if value:
                body.append(f"<p>{html.escape(value)}</p>")
            para.clear()

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("%") or line.startswith("%%"):
            flush_para()
            continue
        if line.startswith("\\begin{tabular}"):
            flush_para()
            in_table = True
            table_lines = []
            continue
        if line.startswith("\\end{tabular}"):
            in_table = False
            table_html = table_to_html(table_lines)
            if table_html:
                body.append(table_html)
            continue
        if in_table:
            table_lines.append(line)
            continue
        if line.startswith("\\begin{itemize}") or line.startswith("\\begin{enumerate}"):
            flush_para()
            in_itemize = True
            body.append("<ul>")
            continue
        if line.startswith("\\end{itemize}") or line.startswith("\\end{enumerate}"):
            flush_para()
            if in_itemize:
                body.append("</ul>")
            in_itemize = False
            continue
        m = re.match(r"\\(section|subsection|subsubsection)\{(.+)\}", line)
        if m:
            flush_para()
            level = {"section": 1, "subsection": 2, "subsubsection": 3}[m.group(1)]
            body.append(f"<h{level}>{html.escape(clean_inline(m.group(2)))}</h{level}>")
            continue
        m = re.match(r"\\paragraph\{(.+)\}", line)
        if m:
            flush_para()
            body.append(f"<h4>{html.escape(clean_inline(m.group(1)))}</h4>")
            continue
        m = re.match(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", line)
        if m:
            flush_para()
            src = m.group(1)
            body.append(f'<p><img src="{html.escape(src)}" style="max-width:100%;"></p>')
            continue
        if line.startswith("\\item"):
            flush_para()
            item = clean_inline(line.removeprefix("\\item"))
            body.append(f"<li>{html.escape(item)}</li>")
            continue
        if line.startswith("\\begin{") or line.startswith("\\end{") or line.startswith("\\centering"):
            flush_para()
            continue
        para.append(line)

    flush_para()
    html_text = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
body { font-family: Aptos, Arial, sans-serif; font-size: 11pt; line-height: 1.35; }
h1 { font-size: 20pt; }
h2 { font-size: 16pt; }
h3 { font-size: 13pt; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th, td { border: 1px solid #777; padding: 4px 6px; vertical-align: top; }
th { background: #eeeeee; }
img { max-width: 100%; height: auto; }
</style>
</head>
<body>
""" + "\n".join(body) + "\n</body>\n</html>\n"
    html_path.write_text(html_text, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: latex_to_word_html.py input.tex output.html")
    convert(Path(sys.argv[1]), Path(sys.argv[2]))
