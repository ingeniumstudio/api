import os

from litestar import MediaType
from litestar import Response
from litestar import Request
from litestar import get
from litestar import post
from litestar.datastructures import Headers


from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN

from litestar.response import Template

from functions import get_dhammapada
from functions import text_to_image
from functions import ntfy_client
from functions import box as box_function
from functions import cowsay as cowsay_function
from functions import fortune as fortune_function
from functions import git_pull_repo
from functions import verify_github_webhook_signature
from functions import process_github_webhook
from functions import get_pids_in_port
from functions import do_reboot

import secret_config

from aux.logging import logging_config


from aux.params import param_optional_text
from aux.params import param_required_text
from aux.params import param_padding
from aux.params import param_foreground_color
from aux.params import param_background_color
from aux.params import param_font_size
from aux.params import param_box
from aux.params import param_cowsay
from aux.params import param_fortune
from aux.params import param_dhammapada_number
from aux.params import param_dhammapada_format

from database import Text

#  DEBUG = True
DEBUG = False

noauth = {"exclude_from_auth": True}


@get("/", include_in_schema=False)
async def hello_world() -> dict[str, str]:
    """Handler function that returns a greeting dictionary."""
    return {"hello": "world!"}


@get("/display-dhammapada",
        media_type=MediaType.TEXT,
        summary="displays dhammapada",
        description="Display a random verse from the Dhammapada if `number` is not specified, verse `number` otherwise",
        **noauth,
        )
async def display_dhammapada(number: param_dhammapada_number = None,
                             format: param_dhammapada_format = None,
                             padding: param_padding = 22,
                             foreground_color: param_foreground_color = "white",
                             background_color: param_background_color = "black",
                             font_size: param_font_size = 16,
                             box: param_box = False
                             ) -> str | Response:

    dhammapada = get_dhammapada(number=number)

    if box:
        text = box_function(text=dhammapada)
    else:
        text = dhammapada

    if format == "png":
        png_bytes = text_to_image(text=text,
                                  padding=padding,
                                  foreground_color=foreground_color,
                                  background_color=background_color,
                                  font_size=font_size
                                  )

        return Response(
            content=png_bytes,
            media_type="image/png",
            headers=Headers({"Content-Disposition":
                             "inline; filename=image.png"})
        )

    return text


@get("/text-to-image",
        summary="image from text",
        description="Generates an image from `text`.",
        **noauth,
        )
async def text_to_img(
                      text: param_optional_text,
                      padding: param_padding = 0,
                      foreground_color: param_foreground_color = "white",
                      background_color: param_background_color = "black",
                      font_size: param_font_size = 16,
                      box: param_box = False,
                      cowsay: param_cowsay = False,
                      fortune: param_fortune = False,
                      ) -> Response:

    if fortune or not text:
        text = fortune_function()

    if cowsay:
        text = cowsay_function(text=text)

    if box:
        text = box_function(text=text)

    png_bytes = text_to_image(text=text,
                              padding=padding,
                              foreground_color=foreground_color,
                              background_color=background_color,
                              font_size=font_size
                              )

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers=Headers({"Content-Disposition":
                         "inline; filename=image.png"})
    )


@get("/cowsay",
     media_type=MediaType.TEXT,
     summary="cowsay text",
     description="Cowsays `text`",
     **noauth,
     )
async def get_cowsay(text: param_required_text) -> str:
    cowsaying = cowsay_function(text=text)

    return cowsaying


@get("/box",
     media_type=MediaType.TEXT,
     summary="text inside box",
     description="Displays `text` inside box",
     **noauth,
     )
async def get_box(text: param_required_text) -> str:
    text_box = box_function(text=text)

    return text_box


@get("/fortune",
     media_type=MediaType.TEXT,
     summary="displays fortune",
     description="Displays a random fortune",
     **noauth,
     )
async def get_fortune() -> str:
    fortune_text = fortune_function()

    return fortune_text


@get("/specific",
     media_type=MediaType.TEXT,
     summary="displays specific fortune",
     description="Displays a chosen fortune",
     **noauth,
     )
async def get_specific() -> str:
    texts = await Text.select()
    specific_text = "\n\n".join([f"{text['id']}: {text['text']}"
                                 for text in texts])

    return specific_text


@get("/index",
     media_type=MediaType.HTML,
     summary="template",
     description="Testing templates",
     **noauth)
async def get_index(text: param_required_text) -> Template:
    context = {"text": text}

    index = Template(template_name="index.html.jinja2", context=context)
    return index


@post("/webhook-github", include_in_schema=False, **noauth)
async def github_webhook_notify(request: Request, data: dict) -> str:
    signature_header = request.headers.getone("X-Hub-Signature-256", "=")
    data_bytes = await request.body()

    if verify_github_webhook_signature(data_bytes=data_bytes,
                                       webhook_secret=secret_config\
                                                      .GITHUB_WEBHOOK_SECRET,
                                       signature=signature_header):

        data_dict = data
        message = process_github_webhook(data=data_dict)

        ntfy_client(message=message, title="from /webhook-github",
                    priority="default")

        git_message = git_pull_repo(data)
        if git_message:
            ntfy_client(message=git_message, title="git pull 'repo'",
                        priority="default")

        return message

    else:
        message = "error checking"

        ntfy_client(message=message, title="from /webhook-github",
                    priority="high")

        raise HTTPException(detail="Invalid signature",
                status_code=HTTP_403_FORBIDDEN)


@get("/reboot")
async def reboot() -> str:
    do_reboot()

    return ""



