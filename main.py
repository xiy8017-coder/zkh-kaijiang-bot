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
    ["历史开奖", "遗漏统计"],
    ["组合统计", "数字统计"],
    ["数据查询", "开奖提醒"],
    ["使用帮助"],
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
    context.user_data.clear()

    await update.message.reply_text(
        "🎯 ZKH 开奖助手\n\n"
        "📊 实时开奖数据\n"
        "📈 历史走势统计\n"
        "⌛ 遗漏数据查询\n"
        "🔢 数字与组合统计\n\n"
        "请选择下面的功能：",
        reply_markup=MARKUP,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙️ 使用帮助\n\n"
        "◎ 最新开奖：查看最近一期开奖\n"
        "◎ 近期走势：查看最近10期开奖\n"
        "◎ 历史开奖：输入期号查询\n"
        "◎ 遗漏统计：查看历史遗漏数据\n"
        "◎ 组合统计：统计大/小、单/双及四种组合\n"
        "◎ 数字统计：统计0～27近期出现次数\n"
        "◎ 数据查询：输入期号查询开奖\n"
        "◎ 开奖提醒：提醒功能开发中\n\n"
        "本机器人提供开奖结果及历史统计数据。"
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

        lines = [
            "📊 最近10期开奖",
            "",
            "期号        开奖号码       组合",
            "━━━━━━━━━━━━━━━━"
        ]

        for item in data:
            lines.append(
                f"{item.get('nbr', '-')}  "
                f"{item.get('number', '-')}  "
                f"{item.get('combination', '-')}"
            )

        lines.append("")
        lines.append("以上为历史开奖结果。")

        await update.message.reply_text(
            "\n".join(lines)
        )

    except Exception:
        await update.message.reply_text(
            "⚠️ 获取近期走势失败，请稍后再试。"
        )


async def query_period(
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


async def combination_stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        body = await api_get_async(
            "/api/kj.json",
            {"nbr": 20}
        )

        data = body.get("data") or []

        if not data:
            await update.message.reply_text(
                "暂时没有统计数据。"
            )
            return

        big = 0
        small = 0
        odd = 0
        even = 0

        combos = {
            "大单": 0,
            "大双": 0,
            "小单": 0,
            "小双": 0,
        }

        for item in data:
            combo = item.get("combination", "")

            if "大" in combo:
                big += 1

            if "小" in combo:
                small += 1

            if "单" in combo:
                odd += 1

            if "双" in combo:
                even += 1

            if combo in combos:
                combos[combo] += 1

        text = (
            "📊 最近20期组合统计\n\n"
            f"大：{big}次\n"
            f"小：{small}次\n"
            f"单：{odd}次\n"
            f"双：{even}次\n\n"
            f"大单：{combos['大单']}次\n"
            f"大双：{combos['大双']}次\n"
            f"小单：{combos['小单']}次\n"
            f"小双：{combos['小双']}次\n\n"
            f"统计样本：{len(data)}期\n"
            "以上为历史统计，不代表下一期结果。"
        )

        await update.message.reply_text(text)

    except Exception:
        await update.message.reply_text(
            "⚠️ 获取组合统计失败，请稍后再试。"
        )


async def number_stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        body = await api_get_async(
            "/api/kj.json",
            {"nbr": 20}
        )

        data = body.get("data") or []

        counts = {
            str(i): 0 for i in range(28)
        }

        for item in data:
            number_text = item.get("number", "")
            parts = number_text.split("=")[0].split("+")

            for part in parts:
                part = part.strip()

                if part.isdigit():
                    number = int(part)

                    if 0 <= number <= 27:
                        counts[str(number)] += 1

        lines = [
            "🔢 最近20期数字统计",
            "",
        ]

        for start_num in range(0, 28, 7):
            row = []

            for number in range(start_num, min(start_num + 7, 28)):
                row.append(
                    f"{number}:{counts[str(number)]}"
                )

            lines.append("   ".join(row))

        lines.append("")
        lines.append("统计范围：最近20期开奖")
        lines.append("仅为历史数据统计。")

        await update.message.reply_text(
            "\n".join(lines)
        )

    except Exception:
        await update.message.reply_text(
            "⚠️ 获取数字统计失败，请稍后再试。"
        )


async def omission_stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        body = await api_get_async(
            "/api/kj.json",
            {"nbr": 100}
        )

        data = body.get("data") or []

        if not data:
            await update.message.reply_text(
                "暂时没有遗漏数据。"
            )
            return

        # 统计四种组合距离最近一次出现的期数
        combo_names = [
            "大单",
            "大双",
            "小单",
            "小双",
        ]

        omissions = {}

        for combo in combo_names:
            omission = 0

            for item in data:
                if item.get("combination") == combo:
                    break
                omission += 1

            omissions[combo] = omission

        # 大小单双遗漏
        big_omission = 0
        small_omission = 0
        odd_omission = 0
        even_omission = 0

        for item in data:
            combo = item.get("combination", "")

            if "大" in combo:
                break

            big_omission += 1

        for item in data:
            combo = item.get("combination", "")

            if "小" in combo:
                break

            small_omission += 1

        for item in data:
            combo = item.get("combination", "")

            if "单" in combo:
                break

            odd_omission += 1

        for item in data:
            combo = item.get("combination", "")

            if "双" in combo:
                break

            even_omission += 1

        text = (
            "⌛ 历史遗漏统计\n\n"
            f"大：遗漏{big_omission}期\n"
            f"小：遗漏{small_omission}期\n"
            f"单：遗漏{odd_omission}期\n"
            f"双：遗漏{even_omission}期\n\n"
            f"大单：遗漏{omissions['大单']}期\n"
            f"大双：遗漏{omissions['大双']}期\n"
            f"小单：遗漏{omissions['小单']}期\n"
            f"小双：遗漏{omissions['小双']}期\n\n"
            "以上为历史遗漏数据，不代表下一期结果。"
        )

        await update.message.reply_text(text)

    except Exception:
        await update.message.reply_text(
            "⚠️ 获取遗漏数据失败，请稍后再试。"
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
        await query_period(update, context, text)
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

    elif text == "遗漏统计":
        await omission_stats(update, context)

    elif text == "组合统计":
        await combination_stats(update, context)

    elif text == "数字统计":
        await number_stats(update, context)

    elif text == "数据查询":
        context.user_data["awaiting_period"] = True

        await update.message.reply_text(
            "🔎 数据查询\n\n"
            "请输入开奖期号：\n"
            "例如：3481125"
        )

    elif text == "开奖提醒":
        await reminder(update, context)

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
