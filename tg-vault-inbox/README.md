# tg-vault-inbox

Telegram-бот → пишет сообщения в Obsidian Vault (`Projects/_inbox`).

## Setup (Mac)

```bash
cd tg-vault-inbox
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

В `.env`:

```env
BOT_TOKEN=...токен от BotFather...
VAULT_PATH=/Users/mr.anderson/Documents/Obsidian Vault
```

Запуск:

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

## Дальше

Открой digest в Cursor (папка vault) и попроси:

```text
Собери из этого digest обновлённый Projects/<project>/context.md
```
