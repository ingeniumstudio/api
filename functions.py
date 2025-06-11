import json
import os
import random
import subprocess

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

if os.path.isfile("secret_config.py"):
    import secret_config

def get_dhammapada(number: int | None = None):
    DHAMMAPADA_JSON_FILEPATH = "./dhammapada.json"

    with open(DHAMMAPADA_JSON_FILEPATH, "r") as dhammapada_json_file:
        dhammapada_json = json.load(dhammapada_json_file)

    if number:
        for key, (verses, verse) in dhammapada_json.items():
            current_key = key
            verse_numbers = verses
            verse = verse

            if number in verses:
                break
    else:
        keys = dhammapada_json.keys()
        random_choice = random.choice(list(keys))

        verse_numbers, verse = dhammapada_json[random_choice]

    verses = ", ".join([str(verse_number) for verse_number in verse_numbers])
    signature = f"- Dhammapada {verses}"
    #  signature = f"— Dhammapada {verses}"

    text_width = max([len(line) for line in verse.splitlines()])
    offset_len = text_width - len(signature)
    offset = ' ' * offset_len
    return f"{verse}\n\n{offset}{signature}"
    #  print(verse, signature, sep="\n\n")


def text_to_image(text: str,
                  padding: int = 0,
                  foreground_color: str = "white",
                  background_color: str= "black",
                  font_size: int = 16):

    png_bytes = bytes()
    text = bytes(text, "utf-8").decode("unicode_escape")
    #  text = text.replace('\\n', '\n')

    with Drawing() as draw:
        draw.font =  "./font.ttf"
        #  draw.font =  "/usr/share/fonts/truetype/inconsolata/Inconsolata.otf"
        #  draw.font_size = 16
        draw.font_size = font_size
        #  draw.fill_color = Color("white")
        draw.fill_color = Color(foreground_color)

        # Create a temporary image to measure the text
        with Image(width=1, height=1) as temp_img:
            metrics = draw.get_font_metrics(temp_img, text, multiline=True)
            text_width = int(metrics.text_width)
            text_height = int(metrics.text_height)

        #  padding = 10
        img_width = text_width + padding * 2
        img_height = text_height + padding * 2

        with Image(width=img_width,
                   height=img_height,
                   background=Color(background_color)) as img:
                   #  background=Color('black')) as img:

            draw.text(padding, int(img_height / 2 - text_height / 2 + metrics.ascender), text)

            draw(img)
            if padding == 0:
                img.trim()
            img.sharpen(radius=1, sigma=0.5)

            #  img.format = 'png'
            png_bytes = img.make_blob(format='png')

    return png_bytes


def ntfy_cli(message, title, priority):

    ntfy_server_hostname = secret_config.NTFY_SERVER_HOSTNAME
    ntfy_topic = secret_config.NTFY_TOPIC
    os.environ["NTFY_URL_HTTPS"] = f"https://{ntfy_server_hostname}/{ntfy_topic}"
    os.environ["NTFY_AUTH_TOKEN"] = secret_config.NTFY_TOKEN
    args = ["/home/u07/.venv/bin/python",
            "/home/u07/bin/ntfy-cli.py",
            "--message",
            message,
            "--title",
            title,
            "--priority",
            priority,
            ]
    #  args = ["ntfy-cli.py", "--message", data]
    subprocess.run(args)
