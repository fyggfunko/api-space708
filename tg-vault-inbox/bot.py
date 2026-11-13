#!/usr/bin/env python3
"""Telegram → Obsidian Vault inbox collector.

Saves group/chat messages into Projects/_inbox and can build a daily digest.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
VAULT_PATH = Path(os.getenv("VAULT_PATH", "")).expanduser()
INBOX_DIR = VAULT_PATH / "Projects" / "_inbox"
MAP_FILE = Path(__file__).resolve().parent / ".chat-map.json"


def require_config() -> None:
    if not BOT_TOKEN or BOT_TOKEN.endswith("replace-me"):
        raise SystemExit("Set BOT_TOKEN in .env")
    if not str(VAULT_PATH):
        raise SystemExit("Set VAULT_PATH in .env")
    INBOX_DIR.mkdir(parents=True, exist_ok=True)


def load_map() -> dict:
    if MAP_FILE.exists():
        return json.loads(MAP_FILE.read_text(encoding="utf-8"))
    return {}


def save_map(data: dict) -> None:
    MAP_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"[\s_-]+", "-", value).strip("-")
    return value or "chat"


def chat_label(update: Update) -> str:
    chat = update.effective_chat
    mapping = load_map()
    key = str(chat.id)
    if key in mapping:
        return mapping[key]
    title = chat.title or chat.username or chat.full_name or key
    return slugify(str(title))


def inbox_file(update: Update, day: str | None = None) -> Path:
    day = day or datetime.now().strftime("%Y-%m-%d")
    label = chat_label(update)
    return INBOX_DIR / f"{day}__{label}.md"


def append_line(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        header = (
            f"# Inbox {path.stem}\n\n"
            f"tags: [tg, inbox]\n\n"
        )
        path.write_text(header, encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Бот пишет сообщения в Obsidian Projects/_inbox.\n"
        "Команды:\n"
        "/ping — проверка\n"
        "/where — путь inbox\n"
        "/link <проект> — привязать этот чат к проекту\n"
        "/digest — собрать выжимку за сегодня"
    )


async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("pong")


async def cmd_where(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"VAULT: {VAULT_PATH}\nINBOX: {INBOX_DIR}")


async def cmd_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Использование: /link название-проекта")
        return
    project = slugify(" ".join(context.args))
    mapping = load_map()
    mapping[str(update.effective_chat.id)] = project
    save_map(mapping)
    project_dir = VAULT_PATH / "Projects" / project
    project_dir.mkdir(parents=True, exist_ok=True)
    context_file = project_dir / "context.md"
    if not context_file.exists():
        context_file.write_text(
            (
                "---\n"
                f"project: {project}\n"
                "tags: [project, context]\n"
                f"updated: {datetime.now().strftime('%Y-%m-%d')}\n"
                "---\n\n"
                f"# {project}\n\n"
                "## Цель\n-\n\n"
                "## Сейчас в работе\n-\n\n"
                "## Решения\n-\n\n"
                "## Открытые вопросы\n-\n\n"
                "## Источники\n"
                f"- TG chat id: {update.effective_chat.id}\n"
            ),
            encoding="utf-8",
        )
    await update.message.reply_text(f"Чат привязан к проекту `{project}`")


async def cmd_digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    day = datetime.now().strftime("%Y-%m-%d")
    label = chat_label(update)
    src = INBOX_DIR / f"{day}__{label}.md"
    if not src.exists():
        await update.message.reply_text("За сегодня сообщений ещё нет.")
        return
    text = src.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.startswith("- ")]
    digest_path = INBOX_DIR / f"{day}__{label}__digest.md"
    body = [
        f"# Digest {day} · {label}",
        "",
        f"Сообщений: {len(lines)}",
        "",
        "## Сырые пункты",
        "",
        *lines,
        "",
        "## Черновик контекста",
        "",
        "- Ключевые темы:",
        "- Решения:",
        "- Next:",
        "",
    ]
    digest_path.write_text("\n".join(body), encoding="utf-8")
    await update.message.reply_text(
        f"Digest сохранён: Projects/_inbox/{digest_path.name}\n"
        "Открой его в Cursor/Obsidian и попроси сделать project context."
    )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if not msg or not msg.text:
        return
    if msg.text.startswith("/"):
        return
    user = update.effective_user
    author = user.username or user.full_name or str(user.id)
    ts = datetime.now().strftime("%H:%M")
    line = f"- [{ts}] @{author}: {msg.text}"
    path = inbox_file(update)
    append_line(path, line)


def main() -> None:
    require_config()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.add_handler(CommandHandler("where", cmd_where))
    app.add_handler(CommandHandler("link", cmd_link))
    app.add_handler(CommandHandler("digest", cmd_digest))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    print(f"Bot started. Inbox → {INBOX_DIR}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
