import os
import json
import asyncio
from urllib.request import Request, urlopen
from urllib.parse import urlencode

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("YU28_API_KEY")

API_BASE = "https://yu28.top"

KEYBOARD = [
    ["最新开奖", "近期走势"],
    ["历史开奖", "开奖提醒"],
    ["组合统计", "使用帮助"],
]

MARKUP = ReplyKeyboardMarkup(
    KEYBOARD,
    resize_keyboard=True
)


def api_get(path, params=None):
    if not API_KEY:
        raise RuntimeError("YU28_API_KEY 未配置")

    url = API_BASE + path

    if params:
        url += "?" + urlencode(params)

    request = Request(
        url,
        headers={
            "X-Api-Key": API_KEY,
            "Accept": "application/json",
        },
    )

    with urlopen(request, timeout=15) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


async def api_get_async(path, params=None):
    return await asyncio.to_thread(
        api_get,
        path,
        params
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_period"] = False

    await update.message.reply_text(
        "🎯 欢迎使用 ZKH 开奖助手\n\n"
        "📊 提供最新开奖信息、历史走势查询\n"
        "🔔 提供开奖提醒与数据统计\n\n"
        "请选择下面的功能：",
        reply_markup=MARKUP,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 使用帮助\n\n"
        "◎ 最新开奖：查看最近一期开奖\n"
        "◎ 近期走势：查看最近10期开奖\n"
        "◎ 历史开奖：输入期号查询\n"
        "◎ 开奖提醒：提醒功能开发中\n"
        "◎ 组合统计：统计最近20期历史组合\n\n"
        "本机器人只提供开奖结果及历史统计数据。"
    )


async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        body = await api_get_async(
            "/api/kj.json",
            {"nbr": 1}
        )

        data = body.get("data") or []

        if not data:
            await update.message.reply_text(
                "暂时没有获取到开奖数据，请稍后再试。"
            )
            return

        item = data[0]

        text = (
            "◎ 最新开奖\n\n"
            f"期号：第{item.get('nbr', '-')}期\n"
            f"时间：{item.get('time', '-')}\n"
            f"号码：{item.get('number', '-')}\n"
            f"组合：{item.get('combination', '-')}\n"
        )

        countdown = body.get("countdown")

        if countdown:
            text += f"下期倒计时：{countdown}\n"

        text += "\n数据仅用于开奖结果查询。"

        await update.message.reply_text(text)

    except Exception:
        await update.message.reply_text(
            "⚠️ 获取开奖数据失败，请稍后再试。"
        )


async def trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        body = await api_get_async(
            "/api/kj.json",
            {"nbr": 10}
        )

        data = body.get("data") or []

        if not data:
            await update.message.reply_text(
                "暂时没有获取到近期数据。"
            )
            return

        lines = ["📊 近期走势\n"]

        for item in data:
            lines.append(
                f"第{item.get('nbr', '-')}期  "
                f"{item.get('number', '-')}  "
                f"{item.get('combination', '-')}"
            )

        lines.append("")
        lines.append("以上为最近10期开奖数据。")

        await update.message.reply_text(
            "\n".join(lines)
        )

    except Exception:
        await update.message.reply_text(
            "⚠️ 获取近期走势失败，请稍后再试。"
        )


async def history_query(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    period: str
):
    if not period.isdigit():
        await update.message.reply_text(
            "请输入正确的期号，例如：3481125"
        )
        return

    try:
        body = await api_get_async(
            "/api/qh.json",
            {"nbr": period}
        )

        data = body.get("data") or []

        if not data:
            await update.message.reply_text(
                f"没有找到第{period}期开奖数据。"
            )
            return

        item = data[0]

        text = (
            "📜 历史开奖\n\n"
            f"期号：第{item.get('nbr', period)}期\n"
            f"时间：{item.get('time', '-')}\n"
            f"号码：{item.get('number', '-')}\n"
            f"组合：{item.get('combination', '-')}"
        )

        await update.message.reply_text(text)

    except Exception:
        await update.message.reply_text(
            "⚠️ 查询失败，请确认期号是否正确。"
        )

    finally:
        context.user_data["awaiting_period"] = False


async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        body = await api_get_async(
            "/api/kj.json",
            {"nbr": 20}
        )

        data = body.get("data") or []

        if not data:
            await update.message.reply_text(
                "暂时没有获取到统计数据。"
            )
            return

        counts = {}

        for item in data:
            combination = item.get("combination", "-")
            counts[combination] = counts.get(combination, 0) + 1

        order = [
            "大单",
            "大双",
            "小单",
            "小双"
        ]

        lines = [
            "📊 最近20期组合统计",
            ""
        ]

        for combination in order:
            lines.append(
                f"{combination}：{counts.get(combination, 0)}次"
            )

        lines.append("")
        lines.append(
            f"统计样本：{len(data)}期"
        )
        lines.append(
            "以上仅为历史开奖统计，不代表下一期结果。"
        )

        await update.message.reply_text(
            "\n".join(lines)
        )

    except Exception:
        await update.message.reply_text(
            "⚠️ 获取组合统计失败，请稍后再试。"
        )


async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔔 开奖提醒\n\n"
        "提醒功能正在开发中。"
    )


async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text.strip()

    if context.user_data.get("awaiting_period"):
        await history_query(update, context, text)
        return

    if text == "最新开奖":
        await latest(update, context)

    elif text == "近期走势":
        await trend(update, context)

    elif text == "历史开奖":
        context.user_data["awaiting_period"] = True

        await update.message.reply_text(
            "📜 请输入你要查询的期号：\n\n"
            "例如：3481125"
        )

    elif text == "开奖提醒":
        await reminder(update, context)

    elif text == "组合统计":
        await statistics(update, context)

    elif text == "使用帮助":
        await help_command(update, context)

    else:
        await update.message.reply_text(
            "请选择下面的功能按钮。",
            reply_markup=MARKUP,
        )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN 未配置")

    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
