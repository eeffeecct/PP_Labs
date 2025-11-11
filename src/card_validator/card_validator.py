import re
import requests

CARD_REGEX = re.compile(
    r'^(?:'
    r'4[0-9]{12}(?:[0-9]{3,6})?|'  # Visa: нач с 4, 13-19 
    r'2[2-7][0-9]{14}|5[1-5][0-9]{14}|'  # Mastercard: 2221-2720 или 51-55, 16ч 
    r'62[0-9]{14,17}|'  # UnionPay: 16-19ч нач с 62
    r'220[0-4][0-9]{12}'  # Mir: 16ч нач с 2200-2204
    r')$'
)


def luhn_checksum(card_num):
    # начиная с конца каждую вторую цифру удвоить, если получилось больше 9 то заменить на сумму его цифр
    # сложить все цифры если % 10 == 0 то ок
    cleaned = clean_card_number(card_num)
    if not cleaned.isdigit():
        return False
    digits = [int(d) for d in cleaned]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0

def clean_card_number(card_num):
    return re.sub(r'[- ]', '', card_num)

def is_valid_card_syntax(card_num):
    cleaned = clean_card_number(card_num)
    return cleaned.isdigit()

def main():
    mode = input("input/url/file: ").strip().lower()
    print("Mode:", mode)

if __name__ == "__main__":
    main()
