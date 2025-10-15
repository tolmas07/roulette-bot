from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS, ROULETTE_GIF
import asyncio

class Handlers:
    def __init__(self, db, game):
        self.db = db
        self.game = game
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or ""
        text = update.message.text.lower().strip()
        
        # Обновляем базу данных для любого пользователя
        balance = self.db.get_balance(user_id)
        self.db.update_username(user_id, username)
        
        # Обработка текстовых команд
        if text == "баланс":
            await self.show_balance(update, user_id, username)
            return
        
        elif text == "история":
            await self.show_history(update, user_id, username)
            return
        
        elif text == "крутить":
            await self.spin_roulette(update, user_id, username)
            return
        
        elif text == "помощь":
            await self.show_help(update, user_id, username)
            return
        
        elif text == "всепользователи" and user_id in ADMIN_IDS:
            await self.admin_all_users(update)
            return
        
        elif text.startswith("изменитьбаланс") and user_id in ADMIN_IDS:
            await self.admin_set_balance(update, text)
            return
        
        # Обработка ставок (число + текст)
        parts = text.split()
        if len(parts) < 2:
            return
        
        try:
            bet_amount = int(parts[0])
            bet_type_str = parts[1]
        except:
            return
        
        if bet_amount > balance:
            await update.message.reply_text(
                "❌ Недостаточно средств для ставки.\n"
                "Для пополнения баланса обращайтесь к админу: @tolmas_prvt"
            )
            return
        
        bet_type_map = {
            "к": "red", "красный": "red", "крас": "red",
            "ч": "black", "черный": "black", "чер": "black", 
            "з": "green", "зеро": "green", "0": "green",
            "чет": "even", "четное": "even",
            "нечет": "odd", "нечетное": "odd", "н": "odd"
        }
        
        if bet_type_str.isdigit():
            bet_type = "number"
            bet_value = bet_type_str
        else:
            bet_type = bet_type_map.get(bet_type_str)
            bet_value = None
        
        if not bet_type:
            await update.message.reply_text("❌ Неизвестный тип ставки")
            return
        
        # Сохраняем ставку в активные
        self.db.set_active_bet(user_id, bet_amount, bet_type, bet_value)
        
        bet_type_display = {
            "red": "🔴 Красный",
            "black": "⚫ Черный", 
            "green": "🟢 Зеро",
            "even": "🔵 Четное",
            "odd": "🟡 Нечетное",
            "number": f"🔢 Число {bet_value}"
        }.get(bet_type, bet_type)
        
        await update.message.reply_text(
            f"✅ Ставка принята!\n"
            f"💎 Сумма: {bet_amount}₿\n"
            f"🎯 Тип: {bet_type_display}\n\n"
            f"Для запуска рулетки напишите: крутить"
        )
    
    async def show_balance(self, update: Update, user_id: int, username: str):
        balance = self.db.get_balance(user_id)
        self.db.update_username(user_id, username)
        await update.message.reply_text(f"💰 Ваш баланс: {balance}₿")
    
    async def show_history(self, update: Update, user_id: int, username: str):
        self.db.update_username(user_id, username)
        
        history = self.db.get_game_history(user_id, 10)
        if not history:
            await update.message.reply_text("📝 История игр пуста")
            return
        
        history_text = "📊 История последних игр:\n\n"
        for winning_number, in history:
            color = "🟢 Зеро" if winning_number in self.game.green else \
                   "🔴 Красный" if winning_number in self.game.red else "⚫ Черный"
            history_text += f"{color} - {winning_number}\n"
        
        await update.message.reply_text(history_text)
    
    async def spin_roulette(self, update: Update, user_id: int, username: str):
        # Проверяем активную ставку
        active_bet = self.db.get_active_bet(user_id)
        if not active_bet:
            await update.message.reply_text("❌ Сначала сделайте ставку! Например: «100 к»")
            return
        
        bet_amount, bet_type, bet_value = active_bet
        
        # Отправляем GIF на 6 секунд
        message = await update.message.reply_animation(
            animation=ROULETTE_GIF,
            caption="🎰 Крутим рулетку..."
        )
        
        # Ждем 6 секунд
        await asyncio.sleep(6)
        
        # Удаляем GIF
        await message.delete()
        
        # Крутим рулетку
        winning_number = self.game.spin()
        win_amount = self.game.calculate_win(bet_type, bet_amount, winning_number, bet_value)
        balance = self.db.get_balance(user_id)
        new_balance = balance - bet_amount + win_amount
        
        # Обновляем баланс и историю
        self.db.update_balance(user_id, new_balance)
        self.db.add_game_history(user_id, username, bet_amount, winning_number, win_amount)
        self.db.clear_active_bet(user_id)
        
        # Определяем цвет
        color = "🟢 ЗЕЛЕНЫЙ" if winning_number in self.game.green else \
               "🔴 КРАСНЫЙ" if winning_number in self.game.red else "⚫ ЧЕРНЫЙ"
        
        # Формируем результат (без баланса)
        result_text = (
            f"🎯 Результат: {winning_number} {color}\n"
            f"👤 Игрок: {username}\n"
            f"💎 Ставка: {bet_amount}₿\n"
            f"💰 Выигрыш: {win_amount}₿"
        )
        
        await update.message.reply_text(result_text)
    
    async def show_help(self, update: Update, user_id: int, username: str):
        self.db.update_username(user_id, username)
        
        help_text = (
            "🎰 ИГРА В РУЛЕТКУ\n\n"
            "💬 Как делать ставки:\n"
            "• «100 к» - 100 на красный (x2)\n"
            "• «50 ч» - 50 на черный (x2)\n"
            "• «25 з» - 25 на зеро (x36)\n"
            "• «10 7» - 10 на число 7 (x36)\n"
            "• «100 чет» - 100 на чет (x2)\n"
            "• «100 нечет» - 100 на нечет (x2)\n\n"
            "📋 Команды:\n"
            "• баланс - проверить баланс\n"
            "• история - история последних игр\n"
            "• крутить - запустить рулетку\n"
            "• помощь - показать эту инструкцию\n\n"
            "🎯 Порядок игры:\n"
            "1. Сделайте ставку (например: 100 к)\n"
            "2. Напишите: крутить\n"
            "3. Смотрите результат!\n\n"
            "❓ При проблемах:\n"
            "Обращайтесь к админу: @tolmas_prvt"
        )
        
        await update.message.reply_text(help_text)
    
    # АДМИН КОМАНДЫ
    async def admin_all_users(self, update: Update):
        all_users = self.db.get_all_users()
        if not all_users:
            await update.message.reply_text("❌ Нет пользователей")
            return
        
        users_text = "📊 Все пользователи:\n\n"
        for user_id, balance, username in all_users:
            username_display = f"@{username}" if username else "Без username"
            users_text += f"ID: {user_id} | {username_display}: {balance}₿\n"
        
        await update.message.reply_text(users_text)
    
    async def admin_set_balance(self, update: Update, text: str):
        try:
            parts = text.split()
            if len(parts) < 3:
                await update.message.reply_text("❌ Формат: изменитьбаланс @username 1000\nИли: изменитьбаланс 123456789 1000")
                return
            
            target = parts[1].replace('@', '')
            new_balance = int(parts[2])
            
            all_users = self.db.get_all_users()
            target_user_id = None
            
            # Поиск по username
            for user_id, balance, db_username in all_users:
                if db_username and db_username.lower() == target.lower():
                    target_user_id = user_id
                    break
            
            # Если не нашли по username, пробуем как ID
            if not target_user_id and target.isdigit():
                target_user_id = int(target)
                # Проверяем что пользователь с таким ID существует
                user_exists = any(user_id == target_user_id for user_id, balance, username in all_users)
                if not user_exists:
                    # Если пользователя нет в базе, создаем его
                    self.db.get_balance(target_user_id)  # Это автоматически создаст пользователя
                    target_user_id = int(target)
            
            if not target_user_id:
                await update.message.reply_text("❌ Пользователь не найден")
                return
            
            self.db.set_balance(target_user_id, new_balance)
            await update.message.reply_text(f"✅ Баланс пользователя {target} установлен: {new_balance}₿")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")