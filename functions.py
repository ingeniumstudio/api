import json
import random

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

def get_dhammapada():
    DHAMMAPADA_JSON_FILEPATH = "./dhammapada.json"

    with open(DHAMMAPADA_JSON_FILEPATH, "r") as dhammapada_json_file:
        dhammapada_json = json.load(dhammapada_json_file)

    keys = dhammapada_json.keys()
    random_choice = random.choice(list(keys))

    verse_numbers, verse = dhammapada_json[random_choice]

    verses = ", ".join([str(verse_number) for verse_number in verse_numbers])
    signature = f"— Dhammapada {verses}"

    return f"{verse}\n\n{signature}"
    #  print(verse, signature, sep="\n\n")


def text_to_image(text: str):

    png_bytes = bytes()
    text = bytes(text, "utf-8").decode("unicode_escape")

    with Drawing() as draw:
        draw.font =  "./font.ttf"
        draw.font_size = 18
        draw.fill_color = Color("white")

        # Create a temporary image to measure the text
        with Image(width=1, height=1) as temp_img:
            metrics = draw.get_font_metrics(temp_img, text, multiline=True)
            text_width = int(metrics.text_width)
            text_height = int(metrics.text_height)

        padding = 10
        img_width = text_width + padding * 2
        img_height = text_height + padding * 2

        with Image(width=img_width, height=img_height, background=Color('black')) as img:

            draw.text(padding, int(img_height / 2 - text_height / 2 + metrics.ascender), text)

            draw(img)
            img.trim()

            #  img.format = 'png'
            png_bytes = img.make_blob(format='png')

    return png_bytes


