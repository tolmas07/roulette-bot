from telegram.ext import Application, MessageHandler, filters
from config import BOT_TOKEN, ADMIN_IDS
from database import Database
from game import RouletteGame
from handlers import Handlers

def main():
    db = Database()
    game = RouletteGame()
    handlers = Handlers(db, game)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Обрабатываем все текстовые сообщения
    app.add_handler(MessageHandler(filters.TEXT, handlers.handle_message))
    
    print("Бот запущен...")
    print(f"Админ ID: {ADMIN_IDS}")
    app.run_polling()

if __name__ == "__main__":
    main()