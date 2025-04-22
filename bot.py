import logging
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, 
    Filters, CallbackContext
)
from telegram.error import BadRequest
import random
import string

# Конфигурация (обновленные данные)
TOKEN = "7726649717:AAEqxQTXyZp-HlasxK5tgX-CIEP2BbjCHZI"
ADMIN_CHAT_ID = -1002376489529  # Теперь с правильным префиксом -100
ADMINS = [5572610919, 5005387093, 5704130500, 5977205680, 1384155668]

# Хранилище вопросов
questions_db = {}
answered_questions = set()

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
    
    qid = generate_question_id()
    questions_db[qid] = {
        'user_id': user.id,
        'username': user.username,
        'question': question_text,
        'answered': False
    }
    
    try:
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📨 Вопрос #{qid} от @{user.username} (ID: {user.id}):\n\n{question_text}\n\n"
                 f"Для ответа используйте команду:\n"
                 f"/answer {qid} [текст ответа]"
        )
        update.message.reply_text(f"✅ Ваш вопрос (ID: {qid}) отправлен руководству!")
    except BadRequest as e:
        logger.error(f"Ошибка отправки в чат: {e}")
        update.message.reply_text("❌ Ошибка при отправке вопроса. Администраторы уведомлены.")
        
        # Уведомление админов
        for admin_id in ADMINS:
            try:
                context.bot.send_message(
                    chat_id=admin_id,
                    text=f"⚠️ Ошибка бота: не могу отправить в чат {ADMIN_CHAT_ID}\n"
                         f"Ошибка: {str(e)}\n\n"
                         f"Новый вопрос от @{user.username}:\n{question_text}"
                )
            except Exception as admin_error:
                logger.error(f"Не удалось уведомить админа {admin_id}: {admin_error}")

def answer(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMINS:
        update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
        
    args = context.args
    if len(args) < 2:
        update.message.reply_text("❌ Используйте: /answer [ID вопроса] [текст ответа]")
        return
    
    qid = args[0]
    answer_text = " ".join(args[1:])
    
    if qid not in questions_db:
        update.message.reply_text("❌ Вопрос с таким ID не найден")
        return
        
    if questions_db[qid]['answered']:
        update.message.reply_text("⚠️ На этот вопрос уже был дан ответ")
        return
    
    try:
        context.bot.send_message(
            chat_id=questions_db[qid]['user_id'],
            text=f"📢 Ответ на ваш вопрос #{qid}:\n\n{answer_text}"
        )
        questions_db[qid]['answered'] = True
        update.message.reply_text(f"✅ Ответ на вопрос #{qid} отправлен пользователю")
    except Exception as e:
        logger.error(f"Error sending answer: {e}")
        update.message.reply_text("❌ Ошибка при отправке ответа")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Команды
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("question", question))
    dp.add_handler(CommandHandler("answer", answer))
    
    # Обработчик ошибок
    def error_handler(update: Update, context: CallbackContext):
        logger.error(f'Update {update} caused error {context.error}')
        
    dp.add_error_handler(error_handler)
    
    updater.start_polling()
    logger.info("Бот запущен и работает...")
    updater.idle()

if __name__ == '__main__':
    main()
