#!/usr/bin/env python3
"""Convert a Telegram Desktop HTML chat export into a vault markdown note."""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path


class ExportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str]] = []
        self.chat_name = ""
        self.messages: list[dict[str, str]] = []
        self.current: dict[str, str] | None = None
        self.capture: str | None = None
        self.capture_depth = 0
        self.buf: list[str] = []
        self.last_author = ""
        self.in_header = False
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        classes = set(attr.get("class", "").split())
        self.stack.append((tag, attr.get("class", "")))
        depth = len(self.stack)

        if tag == "title":
            self.in_title = True
            self._start_capture("chat", depth)
        if tag == "div" and "page_header" in classes:
            self.in_header = True
        if tag == "div" and self.in_header and "name" in classes and "bold" in classes:
            self._start_capture("chat", depth)
        if tag == "div" and self.in_header and classes == {"text", "bold"}:
            self._start_capture("chat", depth)

        if tag == "div" and "message" in classes:
            kind = "service" if "service" in classes else "message"
            self.current = {"type": kind, "author": "", "date": "", "text": ""}
            if kind == "message" and "joined" in classes:
                self.current["author"] = self.last_author
            self.messages.append(self.current)

        if self.current and tag == "div" and "date" in classes and "details" in classes:
            self.current["date"] = attr.get("title", "").strip()

        if self.current and tag == "div" and "from_name" in classes:
            self._start_capture("author", depth)
        elif self.current and tag == "div" and "text" in classes and "bold" not in classes:
            self._start_capture("text", depth)
        elif self.current and tag == "div" and classes == {"body", "details"}:
            self._start_capture("text", depth)
        elif self.current and tag == "div" and "title" in classes and "bold" in classes:
            self._start_capture("file", depth)

        if tag == "br" and self.capture in {"text", "file"}:
            self.buf.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self.capture and len(self.stack) == self.capture_depth:
            self._finish_capture()
        if tag == "title":
            self.in_title = False
        if self.stack:
            ended = self.stack.pop()
            if "page_header" in ended[1].split():
                self.in_header = False

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.buf.append(data)

    def _start_capture(self, field: str, depth: int) -> None:
        if self.capture:
            self._finish_capture()
        self.capture = field
        self.capture_depth = depth
        self.buf = []

    def _finish_capture(self) -> None:
        value = re.sub(r"\n{3,}", "\n\n", "".join(self.buf)).strip()
        field = self.capture
        self.capture = None
        self.buf = []
        if field == "chat" and value and not self.chat_name:
            self.chat_name = value
            return
        if not self.current or not field:
            return
        if field == "author":
            self.current["author"] = value
            if value:
                self.last_author = value
        elif field == "file":
            extra = f"[file] {value}" if value else "[file]"
            self.current["text"] = (self.current["text"] + "\n" + extra).strip()
        else:
            self.current["text"] = (self.current["text"] + "\n" + value).strip() if self.current["text"] else value


def export_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    files = sorted(source.glob("messages*.html"))
    if not files:
        raise SystemExit(f"В {source} нет messages.html")
    return files


def to_markdown(chat_name: str, messages: list[dict[str, str]], source: Path) -> str:
    lines = [
        "---",
        "source: telegram-html-export",
        f"chat: {chat_name}",
        "tags: [tg, inbox, source]",
        "---",
        "",
        f"# {chat_name}",
        "",
        f"Источник: `{source}`",
        "",
    ]
    for message in messages:
        if message["type"] == "service":
            if message["text"]:
                lines.extend([f"## {message['text']}", ""])
            continue
        if not message["text"]:
            continue
        author = message["author"] or "unknown"
        when = message["date"] or ""
        text = message["text"].replace("\n", "\n  ")
        lines.append(f"- [{when}] @{author}: {text}")
    lines.append("")
    return "\n".join(lines)


def convert(source: Path, output: Path) -> tuple[str, int]:
    parser = ExportParser()
    for path in export_files(source):
        parser.feed(path.read_text(encoding="utf-8"))
    chat_name = parser.chat_name or source.stem
    count = sum(1 for message in parser.messages if message["type"] == "message" and message["text"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(to_markdown(chat_name, parser.messages, source), encoding="utf-8")
    return chat_name, count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="messages.html или папка экспорта")
    parser.add_argument("-o", "--output", type=Path, required=True, help="куда записать markdown")
    args = parser.parse_args()
    chat_name, count = convert(args.source, args.output)
    print(f"{chat_name}: {count} сообщений → {args.output}")


if __name__ == "__main__":
    main()
