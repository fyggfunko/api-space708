# tg-vault-inbox

Два режима записи рабочих чатов в Obsidian Vault (`Projects/_inbox`).

- **Свой аккаунт** (`user_collect.py`) — читает чаты, в которых ты уже состоишь, включая историю. Это основной режим.
- **Бот** (`bot.py`) — только новые сообщения в чатах, куда бота добавили.

## Setup (Mac)

```bash
cd tg-vault-inbox
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

В `.env` для своего аккаунта:

```env
API_ID=...
API_HASH=...
VAULT_PATH=/Users/mr.anderson/Documents/Obsidian Vault
CHATS=
HISTORY_LIMIT=100
```

`API_ID` и `API_HASH` берутся на https://my.telegram.org → API development tools. Это не токен бота. Файл сессии `user.session` остаётся только на этом компьютере.

Список чатов:

```bash
python user_collect.py --list
```

Впиши нужные названия в `CHATS` и собери сообщения:

```bash
python user_collect.py
```

При первом запуске Telegram спросит телефон и код в этом терминале. Код и сессию никуда не отправляй.

Бот, если нужен отдельно. Запуск:

```bash
python bot.py
```

## Telegram

1. BotFather → `/setprivacy` → **Disable**
2. Добавь бота в рабочий чат, лучше админом
3. В чате: `/ping`
4. `/link my-project` — привязать чат к проекту
5. Пиши в чат как обычно — сообщения появятся в `Projects/_inbox/`
6. `/digest` — дневная выжимка в `_inbox`

## HTML-экспорт

Telegram Desktop часто отдаёт `messages.html`, а не JSON. Конвертер делает из него markdown-источник:

```bash
python3 convert_html.py "/Users/mr.anderson/Downloads/ChatExport_Performers/messages.html" \
  -o "/Users/mr.anderson/Documents/Obsidian Vault/Projects/_inbox/performers.md"
```

Потом в Cursor, из папки vault:

```text
Прочитай Projects/_inbox/performers.md.
Собери по шаблону Templates/Project Context заметку Projects/performers/context.md.
Сырой экспорт в заметку не копируй.
```

## Дальше

Открой digest в Cursor (папка vault) и попроси:

```text
Собери из этого digest обновлённый Projects/<project>/context.md
```
