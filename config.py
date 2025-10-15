import os

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8285107850:AAEjkLjBAO_0FyTSk9EUkBxV0Axs0_pws8g')
STARTING_BALANCE = int(os.environ.get('STARTING_BALANCE', '1000'))
ADMIN_IDS = [int(x) for x in os.environ.get('ADMIN_IDS', '1039005229').split(',')]
ROULETTE_GIF = os.environ.get('ROULETTE_GIF', 'https://i.imgur.com/SjNdRXI.gif')