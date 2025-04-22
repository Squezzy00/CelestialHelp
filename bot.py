import logging
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, 
    Filters, CallbackContext
)

# Конфигурация
TOKEN = "7726649717:AAEqxQTXyZp-HlasxK5tgX-CIEP2BbjCHZI"
ADMIN_CHAT_ID = 2376489529
ADMINS = [5572610919, 5005387093, 5704130500, 5977205680, 1384155668]

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    help_text = (
        "🤖 Помощник империи CELESTIAL\n\n"
        "Чтобы задать вопрос руководству, используй команду:\n"
        "/вопрос [текст вопроса]\n\n"
        "Твой вопрос будет переадресован администраторам."
    )
    update.message.reply_text(help_text)

def question(update: Update, context: CallbackContext):
    user = update.effective_user
    question_text = " ".join(context.args)
    
    if not question_text:
        update.message.reply_text("❌ Используйте: /вопрос [текст вопроса]")
        return
    
    # Отправка вопроса в админ-чат
    context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📨 Вопрос от @{user.username} (ID: {user.id}):\n\n{question_text}"
    )
    update.message.reply_text("✅ Ваш вопрос отправлен руководству!")

def handle_admin_reply(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMINS:
        return
        
    if update.message.reply_to_message and update.message.chat.id == ADMIN_CHAT_ID:
        original_text = update.message.reply_to_message.text
        try:
            user_id = int(original_text.split("ID: ")[1].split(")")[0])
            context.bot.send_message(
                chat_id=user_id,
                text=f"📢 Ответ от руководства CELESTIAL:\n\n{update.message.text}"
            )
            update.message.reply_text("✅ Ответ отправлен игроку!")
        except Exception as e:
            logger.error(f"Error sending reply: {e}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Команды
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("vopros", question))
    dp.add_handler(CommandHandler("вопрос", question))
    
    # Перехват ответов админа
    dp.add_handler(MessageHandler(
        Filters.text & Filters.chat(ADMIN_CHAT_ID),
        handle_admin_reply
    ))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
