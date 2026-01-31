import datetime
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

DEFAULT_FONT = "RobotoMonoNerdFontMono-Regular.ttf"
DEFAULT_FONT_SIZE = 16

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


def get_dhammapada_qid(show_time=True, space_padding=False) -> str:

    qid_dhammapada_filename = os.path.expanduser("~/.dhammapada-tweet-bot.txt")
    qid_dhammapada = open(qid_dhammapada_filename, "r").read()

    file_modification_time = os.path.getmtime(qid_dhammapada_filename)
    date_time = datetime.datetime.fromtimestamp(file_modification_time)
    formatted_date_time = date_time.strftime("%a %d %b %Y, %I:%M:%S%p GMT-3:00")
    time = f"[{formatted_date_time}]"

    lines = qid_dhammapada.split('\n')
    line_size = max(map(len, lines))  # size of the biggest line
    text_lines = [f"{line:<{line_size if space_padding else 0}}"
                  for line in lines]

    if show_time:
        text_lines.append('')
        text_lines.append(f"{time:>{line_size}}")

    text = '\n'.join(text_lines)

    return text


def text_to_image(text: str,
                  padding: int = 0,
                  foreground_color: str = "white",
                  background_color: str= "black",
                  font_size: int = DEFAULT_FONT_SIZE):

    png_bytes = bytes()

    with Drawing() as draw:
        draw.font = DEFAULT_FONT
        draw.font_size = font_size
        draw.fill_color = Color(foreground_color)

        # Create a temporary image to measure the text
        with Image(width=1, height=1) as temp_img:
            metrics = draw.get_font_metrics(temp_img, text, multiline=True)
            text_width = int(metrics.text_width)
            text_height = int(metrics.text_height)

        img_width = text_width + padding * 2
        img_height = text_height + padding * 2

        with Image(width=img_width,
                   height=img_height,
                   background=Color(background_color)) as img:

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

    return hmac.compare_digest(computed_hash, provided_hash)


#new
def verify_github_signature(data_bytes, webhook_secret, signature):
    #  algo, provided_hash = signature.split('=')
    provided_hash = signature.split('=')

    computed_hash = hmac.new(key=webhook_secret.encode("utf-8"),
                             msg=data_bytes,
                             digestmod=hashlib.sha256).hexdigest()

    return hmac.compare_digest(computed_hash, provided_hash)


#  def process_github_webhook(data):
def github_webhook_info_message(data):

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

        #  args = ["/usr/bin/git", "pull"]
        args = ["sudo", "-u", secret_config.USER, "/usr/bin/git", "pull"]
        git_process = subprocess.run(args, capture_output=True, text=True)

        git_message = f"{git_process.stdout}\n---\n{git_process.stderr}"

        return git_message

    else:
        return None


git_message = """\
stdout:

{git_process.stdout}

---
srderr:

{git_process.stderr}
"""

#  def git_pull_repository(data: dict):
def git_pull_repository(repository_local_directory,
                        user,
                        commit_message,
                        data: dict):

    if not commit_message == "commit":
        return 0

    args = [
            "sudo", "-u", user,
            "/usr/bin/git",
            "-C", repository_local_directory,
            "pull"
            ]
    git_process = subprocess.run(args, capture_output=True, text=True)

    message = git_message.format(git_process=git_process)

    return message


def ntfy_client(message, title, priority):

    args = ["/home/u07/.venv/bin/ntfy-client",
            "pub",
            "--server-hostname", secret_config.NTFY_SERVER_HOSTNAME,
            "--topic", secret_config.NTFY_TOPIC,
            "--token", secret_config.NTFY_TOKEN,
            "--message", message,
            "--title", title,
            "--priority", priority,
            "--icon", secret_config.NTFY_ICON,
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


def get_pids_in_port(port: int | str = 8000):
    args_ss = ["sudo", "ss", "-lptn", f"sport = :{port}"]
    ss_process = subprocess.run(args_ss, capture_output=True, text=True)

    pid_list = [pid.split('=')[1] for pid in ss_process.stdout.split(',')
                if pid.startswith("pid=")]

    return pid_list



def do_reboot():
    SIGNAL = "SIGTERM"

    args_kill = ["sudo", "kill", f"-{SIGNAL}"]
    #  args_kill = ["sudo", "kill", "-9"]

    pid_list = get_pids_in_port(port=8000)

    subprocess.run(args_kill + pid_list)

    return pid_list

