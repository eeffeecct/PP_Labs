import re
import requests

# url tets: https://docs.stripe.com/testing

CARD_REGEX = re.compile(
    r'^(?:'
    r'4[0-9]{12}(?:[0-9]{3,6})?|'  # Visa: нач с 4, 13-19 
    r'2[2-7][0-9]{14}|5[1-5][0-9]{14}|'  # Mastercard: 2221-2720 или 51-55, 16ч 
    r'62[0-9]{14,17}|'  # UnionPay: 16-19ч нач с 62
    r'220[0-4][0-9]{12}'  # Mir: 16ч нач с 2200-2204
    r')$'
)

def clean_card_number(card_num):
    return re.sub(r'[- ]', '', card_num)

def is_valid_card_syntax(card_num):
    # any cards
    cleaned = clean_card_number(card_num)
    if not cleaned.isdigit():
        return False
    return bool(CARD_REGEX.match(cleaned))

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

def find_cards_in_text(text, use_luhn=False):
    potential_matches = re.findall(r'\b(?:\d{4}[- ]?){3}\d{1,15}\b|\b\d{13,19}\b', text)
    valid_cards = []
    for match in potential_matches:
        if is_valid_card_syntax(match) and (not use_luhn or luhn_checksum(match)):
            valid_cards.append(match)
    return valid_cards

def main():
    mode = input("input/url/file: ").strip().lower()
    if mode == 'input':
        card_input = input("Enter card number: ").strip()
        if is_valid_card_syntax(card_input):
            print(f"Valid syntax: {card_input}")
            if luhn_checksum(card_input):
                print("Passes Luhn.")
            else:
                print("Fails Luhn.")
        else:
            print("Invalid syntax.")
    elif mode == 'url':
        url = input("Enter URL: ").strip()
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            cards = find_cards_in_text(response.text, use_luhn=True)
            print(f"Found {len(cards)} valid cards: {cards}")
        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
    elif mode == 'file':
        file_path = input("Enter file path: ").strip()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            cards = find_cards_in_text(content, use_luhn=True)
            print(f"Found {len(cards)} valid cards: {cards}")
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()