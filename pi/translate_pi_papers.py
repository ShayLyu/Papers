#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = "llama3.2:latest"
DEFAULT_FILES = {
    "pi0.pdf": "pi0_纯翻译.md",
    "pi05.pdf": "pi05_纯翻译.md",
    "pistar06.pdf": "pistar06_纯翻译.md",
    "pi07.pdf": "pi07_纯翻译.md",
}


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n\n".join(pages)


def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"/C\d+(?:/C\d+)*", " ", text)
    text = re.sub(r"https?://\S+", lambda m: "\n" + m.group(0) + "\n", text)
    text = re.sub(r"([a-zA-Z])-\n([a-zA-Z])", r"\1\2", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    return text.strip()


def paragraphize(text: str) -> list[str]:
    raw_parts = re.split(r"\n{2,}", text)
    parts: list[str] = []
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        if len(part) < 2:
            continue
        parts.append(part)
    return parts


def chunk_paragraphs(paragraphs: list[str], target_chars: int = 3200) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for para in paragraphs:
        para_len = len(para)
        if current and current_len + para_len > target_chars:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = para_len
        else:
            current.append(para)
            current_len += para_len + 2
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def build_prompt(chunk: str, chunk_idx: int, chunk_total: int) -> str:
    return f"""你是一名严格忠实的学术论文翻译助手。请把下面这段英文论文内容翻译成中文 Markdown，要求：
1. 只输出中文译文，不要解释，不要总结，不要补充说明。
2. 忠实保留原意；术语前后一致。
3. 如果识别到章节标题，请翻译成合适的 Markdown 标题格式，例如 `##`、`###`。
4. 公式、引用编号、图表编号、项目符号、变量名尽量保留。
5. 不要输出英文原文，除非是公式变量、专有名词或确实不宜翻译的缩写。
6. 不要添加“第X部分翻译”等额外字样。

当前片段：{chunk_idx}/{chunk_total}

待翻译内容：

{chunk}
"""


def run_ollama(prompt: str, model: str) -> str:
    proc = subprocess.run(
        ["ollama", "run", model, prompt],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def translate_pdf(pdf_path: Path, output_path: Path, model: str, overwrite: bool) -> None:
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"{output_path} already exists; use --overwrite to replace it")

    raw_text = extract_text(pdf_path)
    clean_text = normalize_text(raw_text)
    paragraphs = paragraphize(clean_text)
    chunks = chunk_paragraphs(paragraphs)

    rendered_chunks: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        print(f"[{pdf_path.name}] translating chunk {idx}/{len(chunks)}", file=sys.stderr)
        translated = run_ollama(build_prompt(chunk, idx, len(chunks)), model=model)
        rendered_chunks.append(translated)

    output = "\n\n".join(rendered_chunks).strip() + "\n"
    output_path.write_text(output, encoding="utf-8")
    print(f"wrote {output_path}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate PI papers to Chinese Markdown with Ollama.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    for pdf_name, md_name in DEFAULT_FILES.items():
        translate_pdf(
            pdf_path=ROOT / pdf_name,
            output_path=ROOT / md_name,
            model=args.model,
            overwrite=args.overwrite,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
