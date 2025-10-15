import random

class RouletteGame:
    def __init__(self):
        self.numbers = list(range(0, 37))
        self.red = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
        self.black = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
        self.green = [0]
    
    def spin(self):
        return random.choice(self.numbers)
    
    def calculate_win(self, bet_type, bet_amount, winning_number, bet_value=None):
        if bet_type == "number":
            return bet_amount * 36 if winning_number == int(bet_value) else 0
        elif bet_type == "red":
            return bet_amount * 2 if winning_number in self.red else 0
        elif bet_type == "black":
            return bet_amount * 2 if winning_number in self.black else 0
        elif bet_type == "green":
            return bet_amount * 36 if winning_number in self.green else 0
        elif bet_type == "even":
            return bet_amount * 2 if winning_number % 2 == 0 and winning_number != 0 else 0
        elif bet_type == "odd":
            return bet_amount * 2 if winning_number % 2 == 1 else 0
        elif bet_type == "1-12":
            return bet_amount * 3 if 1 <= winning_number <= 12 else 0
        elif bet_type == "13-24":
            return bet_amount * 3 if 13 <= winning_number <= 24 else 0
        elif bet_type == "25-36":
            return bet_amount * 3 if 25 <= winning_number <= 36 else 0