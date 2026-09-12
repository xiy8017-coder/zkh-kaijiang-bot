import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")

keyboard = [
    ["最新开奖", "近期走势"],
    ["历史开奖", "开奖提醒"],
    ["数据统计", "使用帮助"],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🎯 欢迎使用 ZKH 开奖助手\n\n"
        "📊 提供开奖信息、历史走势查询\n"
        "🔔 提供开奖提醒与数据统计\n\n"
        "请选择下面的功能：",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 使用帮助\n\n"
        "最新开奖：查看最新开奖信息\n"
        "近期走势：查看近期数据走势\n"
        "历史开奖：查询历史开奖记录\n"
        "开奖提醒：设置开奖提醒\n"
        "数据统计：查看数据统计\n\n"
        "输入 /start 返回主菜单。"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "最新开奖":
        await update.message.reply_text(
            "🎯 最新开奖\n\n"
            "暂无实时数据，请稍后再试。"
        )

    elif text == "近期走势":
        await update.message.reply_text(
            "📈 近期走势\n\n"
            "暂无实时数据，请稍后再试。"
        )

    elif text == "历史开奖":
        await update.message.reply_text(
            "📋 历史开奖\n\n"
            "暂无历史数据，请稍后再试。"
        )

    elif text == "开奖提醒":
        await update.message.reply_text(
            "🔔 开奖提醒\n\n"
            "提醒功能正在完善中。"
        )

    elif text == "数据统计":
        await update.message.reply_text(
            "📊 数据统计\n\n"
            "统计功能正在完善中。"
        )

    elif text == "使用帮助":
        await help_command(update, context)

    else:
        await update.message.reply_text(
            "请输入菜单中的功能，或发送 /help 查看帮助。"
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
