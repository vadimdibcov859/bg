import os.path

import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract'

country = [70, 45, 380, 998, 1, 86, 49, 33, 81, 354, 46, 39]


def detect_county(number):
    for code in country:
        if str(code) == str(number)[:len(str(code))]:
            return code

    return 0


def add_number(number, is_an_apple_num):
    with open('checked_numbers.txt', 'r') as checked_numbers_file:
        if str(number) in checked_numbers_file.read().split():
            return

    country_data_file = f'{detect_county(number)}{["green", "blue"][is_an_apple_num]}.txt'

    if not os.path.exists('data'):
        os.mkdir('data')

    with open(os.path.join('data', country_data_file), 'a') as file:
        file.write(str(number) + '\n')

    with open('checked_numbers.txt', 'a') as checked_numbers_file:
        checked_numbers_file.write(str(number) + '\n')


def clear_number(dirty_number):
    clean_number = ''
    for char in dirty_number:
        if char in '0123456789':
            clean_number += char

    return int(clean_number)


def define_number(screenshot):
    start_y = 270
    start_x = 80
    panel_height = 40

    number_screenshot = screenshot.crop((start_x, start_y, screenshot.width - 200, start_y + panel_height))

    text_end_x = None
    for x in reversed(range(1, number_screenshot.width)):
        if number_screenshot.getpixel((x, int(panel_height / 2))) != (255, 255, 255):
            text_end_x = x
            break

    number_screenshot = number_screenshot.crop((0, 0, text_end_x - 5, panel_height))
    number_screenshot.save('number.png')

    return clear_number(pytesseract.image_to_string('number.png'))


def is_an_imessage_number(screenshot):
    text_screenshot = screenshot.crop((180, 120, 500, 200))

    text_screenshot.save('text.png')

    return 'i' in pytesseract.image_to_string('text.png')


def prepare_screenshot(file_path):
    with Image.open(file_path) as screenshot:
        number = define_number(screenshot)
        is_an_apple_num = is_an_imessage_number(screenshot)

        add_number(number, is_an_apple_num)
