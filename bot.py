import logging
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, 
    Filters, CallbackContext
)
from telegram.error import BadRequest
import random
import string

# Конфигурация
TOKEN = "7726649717:AAEqxQTXyZp-HlasxK5tgX-CIEP2BbjCHZI"
ADMIN_CHAT_ID = 2376489529  # Убедитесь, что этот ID корректен и бот добавлен в чат
ADMINS = [5572610919, 5005387093, 5704130500, 5977205680, 1384155668]

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def generate_question_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def start(update: Update, context: CallbackContext):
    help_text = (
        "🤖 Помощник империи CELESTIAL\n\n"
        "Чтобы задать вопрос руководству, используй команду:\n"
        "/question [текст вопроса]\n\n"
        "Твой вопрос будет переадресован администраторам."
    )
    update.message.reply_text(help_text)

def question(update: Update, context: CallbackContext):
    user = update.effective_user
    question_text = " ".join(context.args)
    
    if not question_text:
        update.message.reply_text("❌ Используйте: /question [текст вопроса]")
        return
    
    try:
        # Отправка вопроса в админ-чат
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📨 Вопрос от @{user.username} (ID: {user.id}):\n\n{question_text}"
        )
        update.message.reply_text("✅ Ваш вопрос отправлен руководству!")
    except BadRequest as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        update.message.reply_text("❌ Ошибка при отправке вопроса. Администраторы уведомлены.")
        
        # Уведомление разработчиков об ошибке
        for admin_id in ADMINS:
            try:
                context.bot.send_message(
                    chat_id=admin_id,
                    text=f"⚠️ Ошибка бота: не могу отправить сообщение в чат {ADMIN_CHAT_ID}\n"
                         f"Ошибка: {str(e)}"
                )
            except Exception as admin_error:
                logger.error(f"Не удалось уведомить админа {admin_id}: {admin_error}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Команды
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("question", question))
    
    # Обработчик ошибок
    def error_handler(update: Update, context: CallbackContext):
        logger.error(f'Update {update} caused error {context.error}')
        
    dp.add_error_handler(error_handler)
    
    updater.start_polling()
    logger.info("Бот запущен и работает...")
    updater.idle()

if __name__ == '__main__':
    main()
