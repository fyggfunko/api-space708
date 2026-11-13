#!/usr/bin/env python3
"""Read selected Telegram chats with your own account and save them to the vault.

This uses a local Telethon session. It only reads chats you are already in
and that you name in CHATS. The session file stays on this machine.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.custom.dialog import Dialog

load_dotenv()

API_ID = os.getenv("API_ID", "").strip()
API_HASH = os.getenv("API_HASH", "").strip()
VAULT_PATH = Path(os.getenv("VAULT_PATH", "")).expanduser()
CHATS = [part.strip() for part in os.getenv("CHATS", "").split(",") if part.strip()]
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "100"))
SESSION_PATH = Path(__file__).resolve().parent / "user"
STATE_FILE = Path(__file__).resolve().parent / ".user-state.json"
INBOX_DIR = VAULT_PATH / "Projects" / "_inbox"


def require_config() -> None:
    if not API_ID.isdigit() or not API_HASH:
        raise SystemExit("Set API_ID and API_HASH in .env (from https://my.telegram.org)")
    if not str(VAULT_PATH):
        raise SystemExit("Set VAULT_PATH in .env")
    INBOX_DIR.mkdir(parents=True, exist_ok=True)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"[\s_-]+", "-", value).strip("-")
    return value or "chat"


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(data: dict) -> None:
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"# Inbox {path.stem}\n\ntags: [tg, inbox]\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        for line in lines:
            handle.write(line.rstrip() + "\n")


def matches(dialog: Dialog, query: str) -> bool:
    title = dialog.name or ""
    username = getattr(dialog.entity, "username", None) or ""
    needle = query.casefold().lstrip("@")
    return needle in {title.casefold(), username.casefold(), str(dialog.id)}


async def list_dialogs(client: TelegramClient) -> None:
    print("Чаты, которые видны этому аккаунту:\n")
    async for dialog in client.iter_dialogs():
        username = getattr(dialog.entity, "username", None)
        suffix = f" @{username}" if username else ""
        print(f"- {dialog.name}{suffix}")


async def collect(client: TelegramClient) -> None:
    if not CHATS:
        raise SystemExit(
            "CHATS пустой. Сначала запусти `python user_collect.py --list`, "
            "потом впиши точные названия чатов в .env через запятую."
        )

    dialogs = []
    async for dialog in client.iter_dialogs():
        dialogs.append(dialog)

    state = load_state()
    for query in CHATS:
        dialog = next((item for item in dialogs if matches(item, query)), None)
        if dialog is None:
            print(f"Не найден чат: {query}")
            continue

        last_id = int(state.get(str(dialog.id), 0))
        fetched = []
        async for message in client.iter_messages(dialog.entity, min_id=last_id, limit=HISTORY_LIMIT):
            if not message.text or message.action:
                continue
            sender = await message.get_sender()
            author = getattr(sender, "username", None) or getattr(sender, "first_name", None) or "unknown"
            moment = message.date.astimezone().strftime("%Y-%m-%d %H:%M")
            fetched.append((message.id, f"- [{moment}] @{author}: {message.text}"))

        fetched.sort(key=lambda item: item[0])
        if not fetched:
            print(f"{dialog.name}: новых сообщений нет")
            continue

        day = datetime.now().strftime("%Y-%m-%d")
        path = INBOX_DIR / f"{day}__{slugify(dialog.name)}.md"
        append_lines(path, [line for _, line in fetched])
        state[str(dialog.id)] = fetched[-1][0]
        save_state(state)
        print(f"{dialog.name}: записано {len(fetched)} → {path}")


async def main() -> None:
    require_config()
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="показать чаты аккаунта")
    args = parser.parse_args()

    client = TelegramClient(str(SESSION_PATH), int(API_ID), API_HASH)
    await client.start()
    try:
        if args.list:
            await list_dialogs(client)
        else:
            await collect(client)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
