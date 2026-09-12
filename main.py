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
    await update.message.reply_text(
        "🎯 欢迎使用 ZKH 开奖助手\n\n"
        "📊 提供开奖信息、历史走势查询\n"
        "🔔 提供开奖提醒与数据统计\n\n"
        "请选择下面的功能：",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 使用帮助\n\n"
        "🟢 最新开奖：查看最新开奖信息\n"
        "📈 近期走势：查看近期数据走势\n"
        "📚 历史开奖：查询历史开奖记录\n"
        "🔔 开奖提醒：设置开奖提醒\n"
        "📊 数据统计：查看数据统计\n\n"
        "输入 /start 返回主菜单。"
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    replies = {
        "最新开奖": "🎯 最新开奖\n\n暂无实时数据，请稍后再试。",
        "近期走势": "📈 近期走势\n\n暂无数据，正在准备数据接口。",
        "历史开奖": "📚 历史开奖\n\n暂无历史数据。",
        "开奖提醒": "🔔 开奖提醒\n\n提醒功能正在开发中。",
        "数据统计": "📊 数据统计\n\n统计功能正在开发中。",
        "使用帮助": "📖 请使用 /help 查看使用说明。",
    }

    await update.message.reply_text(
        replies.get(text, "请输入菜单中的功能，或发送 /help 查看帮助。")
    )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("ZKH 开奖助手已启动")
    app.run_polling()

if __name__ == "__main__":
    main()
