from card_validator import (clean_card_number, is_valid_card_syntax, luhn_checksum, find_cards_in_text, get_card_type)


def test_clean_card_number():
    assert clean_card_number("1234 5678-90123456") == "1234567890123456"
    assert clean_card_number("1234") == "1234"


def test_is_valid_card_syntax_valid_cases():
    assert is_valid_card_syntax("4111 1111 1111 1111")  # Visa
    assert is_valid_card_syntax("5454 5454 5454 5454")      # Mastercard
    assert is_valid_card_syntax("6250 9460 0000 0016")      # UnionPay
    assert is_valid_card_syntax("2200154524587283")      # Mir


def test_is_valid_card_syntax_invalid_cases():
    assert not is_valid_card_syntax("qwert  qwert")
    assert not is_valid_card_syntax("9999999999999999")
    assert not is_valid_card_syntax("1234 5678 9123 4567")


def test_luhn_checksum_valid_and_invalid():
    valid = "4166 6766 6766 6746"  # Visa, passes Luhn
    invalid = "4539578763621487"
    assert luhn_checksum(valid)
    assert not luhn_checksum(invalid)
    assert not luhn_checksum("abcd")


def test_find_cards_in_text_without_luhn():
    text = "Cards: 4111-1111-1111-1111, 1234 5678 9123 4567"
    result = find_cards_in_text(text)
    assert "4111-1111-1111-1111" in result
    assert "1234 5678 9123 4567" not in result


def test_find_cards_in_text_with_luhn():
    text = "Cards: 4917 6100 0000 0000 4539578763621487"
    result = find_cards_in_text(text, use_luhn=True)
    assert "4917 6100 0000 0000" in result
    assert "4539578763621487" not in result


def test_get_card_type_all_cases():
    assert get_card_type("4111111111111111") == "Visa"
    assert get_card_type("2221000000000009") == "Mastercard"
    assert get_card_type("5100000000000000") == "Mastercard"
    assert get_card_type("6200000000000000") == "UnionPay"
    assert get_card_type("2200000000000000") == "Mir"
    assert get_card_type("9999999999999999") == "Unknown"
