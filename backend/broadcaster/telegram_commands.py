import logging
import re
from datetime import datetime, timezone

import httpx
from sqlalchemy import select, delete
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import settings
from db.database import AsyncSessionLocal
from db.models import Subscription

logger = logging.getLogger(__name__)

_ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def _normalize_address(raw: str) -> str | None:
    addr = raw.strip().lower()
    return addr if _ADDR_RE.match(addr) else None


async def cmd_watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/watch 0x... — register a contract for this chat and start monitoring it."""
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /watch 0xYourContractAddress")
        return

    address = _normalize_address(context.args[0])
    if not address:
        await update.message.reply_text(
            "❌ Invalid address. Must be a 42-character hex string starting with 0x."
        )
        return

    chat_id = str(update.effective_chat.id)

    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(Subscription).where(
                Subscription.contract_address == address,
                Subscription.telegram_chat_id == chat_id,
            )
        )
        if existing.scalar_one_or_none():
            await update.message.reply_text(
                f"✅ Already watching `{address[:16]}...`", parse_mode="Markdown"
            )
            return

        session.add(Subscription(
            contract_address=address,
            telegram_chat_id=chat_id,
            label="user-submitted",
            added_at=datetime.now(timezone.utc),
        ))
        await session.commit()

    try:
        headers = {}
        if settings.watch_api_key:
            headers["X-API-Key"] = settings.watch_api_key
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"{settings.self_api_base.rstrip('/')}/watch",
                json={"address": address, "label": "user-submitted"},
                headers=headers,
            )
    except Exception as e:
        logger.warning(f"Failed to register contract with listener: {e}")

    await update.message.reply_text(
        f"🔍 Now watching `{address[:16]}...`\n"
        f"You'll receive alerts for any anomalies detected on this contract.",
        parse_mode="Markdown",
    )


async def cmd_unwatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/unwatch 0x... — stop watching a contract for this chat."""
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /unwatch 0xYourContractAddress")
        return

    address = _normalize_address(context.args[0])
    if not address:
        await update.message.reply_text("❌ Invalid address.")
        return

    chat_id = str(update.effective_chat.id)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            delete(Subscription).where(
                Subscription.contract_address == address,
                Subscription.telegram_chat_id == chat_id,
            )
        )
        await session.commit()

    if result.rowcount:
        await update.message.reply_text(
            f"🛑 Stopped watching `{address[:16]}...`", parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("You weren't watching that contract.")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/status — list contracts watched by this chat."""
    chat_id = str(update.effective_chat.id)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Subscription)
            .where(Subscription.telegram_chat_id == chat_id)
            .limit(20)
        )
        subs = result.scalars().all()

    if not subs:
        await update.message.reply_text("No contracts being watched yet. Use /watch 0x...")
        return

    lines = [f"🔍 Watching {len(subs)} contract(s):\n"]
    lines += [f"• `{s.contract_address}`" for s in subs]
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ <b>Zeham Bot Commands</b>\n\n"
        "/watch 0x... — Watch a contract for anomalies\n"
        "/unwatch 0x... — Stop watching a contract\n"
        "/status — Show all watched contracts\n"
        "/help — Show this message",
        parse_mode="HTML",
    )


async def _post_init(application):
    """Register the bot command menu (ADR-003 §8.2 register_commands)."""
    await application.bot.set_my_commands([
        BotCommand("watch",   "Watch a contract: /watch 0x..."),
        BotCommand("unwatch", "Stop watching: /unwatch 0x..."),
        BotCommand("status",  "Show monitored contracts"),
        BotCommand("help",    "Show help"),
    ])


def build_telegram_app():
    """Build and return the python-telegram-bot Application (command handlers)."""
    app = ApplicationBuilder().token(
        settings.telegram_bot_token).post_init(_post_init).build()
    app.add_handler(CommandHandler("watch",   cmd_watch))
    app.add_handler(CommandHandler("unwatch", cmd_unwatch))
    app.add_handler(CommandHandler("status",  cmd_status))
    app.add_handler(CommandHandler("help",    cmd_help))
    return app
