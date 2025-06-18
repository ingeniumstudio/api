import hmac
import hashlib
import json
import os
import random
import subprocess
import sys

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

import secret_config

#  if os.path.isfile("secret_config.py"):
#      import secret_config


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
    signature = f"— Dhammapada {verses}"
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
    #  text = bytes(text, "utf-8").decode("unicode_escape")
    #text = bytes(text, "utf-8")#.decode("utf-8")
    #  text = text.replace('\\n', '\n')

    with Drawing() as draw:
        #  draw.font =  "./font.ttf"
        draw.font = "RobotoMonoNerdFontMono-Regular.ttf"
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


def verify_github_webhook_signature(data_bytes, webhook_secret, signature):
    algo, provided_hash = signature.split('=')

    computed_hash = hmac.new(key=webhook_secret.encode("utf-8"),
                             msg=data_bytes,
                             digestmod=hashlib.sha256).hexdigest()

    #  if not hmac.compare_digest(computed_hash, provided_hash):
    #      return "error checking"
    #  else:
    #      return "checking ok"
    return hmac.compare_digest(computed_hash, provided_hash)


def process_github_webhook(data):

    #  file_separator = ", "
    file_separator = "\n"

    message = f"""\
Repo: {data["repository"]["full_name"]} ({data["repository"]["visibility"]})
Pusher: {data["pusher"]["name"]}

Date: {data["head_commit"]["timestamp"]}

ａｄｄｅｄ
{file_separator.join([f"  · “{file}”" for file in data["head_commit"]["added"]]) or "—"}

ｒｅｍｏｖｅｄ
{file_separator.join([f"  · “{file}”" for file in data["head_commit"]["removed"]]) or "—"}

ｍｏｄｉｆｉｅｄ
{file_separator.join([f"  · “{file}”" for file in data["head_commit"]["modified"]]) or "—"}

Commit: {data["head_commit"]["url"]}
"""

    return message


def git_pull_repo(data: dict):
    if data["repository"]["full_name"] == secret_config.REPOSITORY_FULL_NAME\
            and data["head_commit"]["message"] == "commit":

        args = ["/usr/bin/git", "pull"]

        git_process = subprocess.run(args, capture_output=True, text=True)

        return git_process.stderr

    else:
        return None


def ntfy_client(message, title, priority):

    args = ["/home/u07/.venv/bin/ntfy-client",
            "pub",
            "--server-hostname",
            secret_config.NTFY_SERVER_HOSTNAME,
            "--topic",
            secret_config.NTFY_TOPIC,
            "--token",
            secret_config.NTFY_TOKEN,
            "--message",
            message,
            "--title",
            title,
            "--priority",
            priority,
            ]
    #  args = ["ntfy-cli.py", "--message", data]
    subprocess.run(args)


def box(text):

    CHARS = { 'horizontal_char': '\u2500',
              'vertical_char': '\u2502',
              'topleft_char': '\u250c',
              'topright_char': '\u2510',
              'bottomleft_char': '\u2514',
              'bottomright_char': '\u2518' }

    NEWLINE = '\n'

    PAD_SIZE = 1
    PAD_CHAR = '\u0020' * PAD_SIZE  # space char


    def process_line(text_line, biggest_line_length, pad_size, pad_char,
                     vertical_char):
        """Adds side border to each line on input.
        """

        padding = pad_char * pad_size
        extra_padding = pad_char * (biggest_line_length - len(text_line))

        return (vertical_char + padding + text_line + extra_padding + padding
                + vertical_char)


    #  line_list = sys.stdin.readlines()
    #  line_list = text.readlines()
    text = text.replace('\\n', '\n')
    line_list = text.split("\n")
    lines = [line.expandtabs().strip('\n') for line in line_list]

    biggest_line_length = max(map(len, lines))

    horizontal_borders_length = biggest_line_length + (PAD_SIZE * 2)

    top_border = (CHARS['topleft_char'] +
                  CHARS['horizontal_char'] * horizontal_borders_length +
                  CHARS['topright_char'])

    bottom_border = (CHARS['bottomleft_char'] +
                     CHARS['horizontal_char'] * horizontal_borders_length +
                     CHARS['bottomright_char'])

    text_with_side_borders_line_list = [process_line(text_line=line,
                                          biggest_line_length=biggest_line_length,
                                          pad_size=PAD_SIZE,
                                          pad_char=PAD_CHAR,
                                          vertical_char=CHARS['vertical_char'])
                                        for line in lines]

    text_with_side_borders = str('\n').join(text_with_side_borders_line_list)
    box_parts = [top_border, text_with_side_borders, bottom_border]

    box = str('\n').join(box_parts)

    return box


def cowsay(text: str):
    command_args = ["/usr/games/cowsay", "-n"]
    cowsay_process = subprocess.run(command_args,
                                    input=text,
                                    capture_output=True,
                                    text=True)

    return cowsay_process.stdout


def fortune():
    command_args = ["/usr/games/fortune"]
    fortune_process = subprocess.run(command_args,
                                     capture_output=True,
                                     text=True)

    #  return fortune_process.stdout
    return fortune_process.stdout.strip("\n")
