import logging
from telegram import Update, Bot
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, 
    Filters, CallbackContext, Dispatcher
)

# Конфигурация
TOKEN = "7726649717:AAEqxQTXyZp-HlasxK5tgX-CIEP2BbjCHZI"  # Замените на токен от @BotFather
ADMIN_CHAT_ID = 2376489529  # Чат для вопросов

# Настройка логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Обработчик команды /вопрос
def question(update: Update, context: CallbackContext):
    user = update.effective_user
    question_text = " ".join(context.args)
    
    if not question_text:
        update.message.reply_text("❌ Используйте: /вопрос [текст]")
        return
    
    # Отправка вопроса в админ-чат
    context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📨 Вопрос от @{user.username} (ID: {user.id}):\n\n{question_text}"
    )
    update.message.reply_text("✅ Ваш вопрос отправлен руководству!")

# Ответ админа (пересылка игроку)
def handle_admin_reply(update: Update, context: CallbackContext):
    if update.message.reply_to_message and update.message.chat.id == ADMIN_CHAT_ID:
        original_text = update.message.reply_to_message.text
        user_id = int(original_text.split("ID: ")[1].split(")")[0])
        
        context.bot.send_message(
            chat_id=user_id,
            text=f"📢 Ответ от руководства:\n\n{update.message.text}"
        )
        update.message.reply_text("✅ Ответ отправлен игроку!")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    # Команды
    dp.add_handler(CommandHandler("вопрос", question, pass_args=True))
    
    # Перехват ответов админа
    dp.add_handler(MessageHandler(Filters.text & Filters.chat(ADMIN_CHAT_ID), handle_admin_reply)
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
