import datetime
import json
import os
from types import NoneType

from litestar import MediaType
from litestar import Response
from litestar import Request
from litestar import get
from litestar import post
from litestar.datastructures import Headers, secret_values

from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_302_FOUND  # temporary redirection
from litestar.status_codes import HTTP_400_BAD_REQUEST
from litestar.status_codes import HTTP_403_FORBIDDEN

from litestar.response import Template
from litestar.response import Redirect

from functions import (
    get_dhammapada,
    text_to_image,
    ntfy_client,
    box as box_function,
    cowsay as cowsay_function,
    fortune as fortune_function,
    git_pull_repository,
    verify_github_signature,
    github_webhook_info_message,
    do_reboot,

    get_dhammapada_qid,
)

from aux.params import (
    param_optional_text,
    param_required_text,
    param_padding,
    param_space_padding,
    param_foreground_color,
    param_background_color,
    param_font_size,
    param_box,
    param_cowsay,
    param_fortune,
    param_dhammapada_number,
    param_dhammapada_format,
)

from database import Text

import secret_config
from secret_webhooks import WEBHOOK_DATA


#  DEBUG = True
DEBUG = False

noauth = {"exclude_from_auth": True}


@get("/",
     include_in_schema=False,
     status_code=HTTP_302_FOUND,
     **noauth,  # pyright: ignore
     )
async def root_path() -> Redirect:
    """Redirects root to Swagger"""

    return Redirect(path="/schema/swagger")


@get("/dhammapada",
     media_type=MediaType.TEXT,
     summary="displays the quarter in die dhammapada",
     description="From our bot",
     **noauth,  # pyright: ignore
     )
async def dhammapada_qid(format: param_dhammapada_format = None,
                         space_padding: param_space_padding = False,
                         ) -> str | Response:

    text = get_dhammapada_qid(show_time=True, space_padding=space_padding)

    if format == "png":
        png_bytes = text_to_image(text=text,
                                  padding=22,
                                  foreground_color="orange",
                                  background_color="#333366",
                                  font_size=14
                                  )
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers=Headers({"Content-Disposition":
                             "inline; filename=image.png"})
        )

    return text


@get("/display-dhammapada",
     media_type=MediaType.TEXT,
     summary="displays dhammapada",
     description="Display a random verse from the Dhammapada if `number` is not specified, verse `number` otherwise",
     **noauth,  # pyright: ignore
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
     **noauth,  # pyright: ignore
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
     **noauth,  # pyright: ignore
     )
async def get_cowsay(text: param_required_text) -> str:
    cowsaying = cowsay_function(text=text)

    return cowsaying


@get("/box",
     media_type=MediaType.TEXT,
     summary="text inside box",
     description="Displays `text` inside box",
     **noauth,  # pyright: ignore
     )
async def get_box(text: param_required_text) -> str:
    text_box = box_function(text=text)

    return text_box


@get("/fortune",
     media_type=MediaType.TEXT,
     summary="displays fortune",
     description="Displays a random fortune",
     **noauth,  # pyright: ignore
     )
async def get_fortune() -> str:
    fortune_text = fortune_function()

    return fortune_text


@get("/specific",
     media_type=MediaType.TEXT,
     summary="displays specific fortune",
     description="Displays a chosen fortune",
     **noauth,  # pyright: ignore
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
     **noauth,  # pyright: ignore
     )
async def get_index(text: param_required_text) -> Template:
    context = {"text": text}

    index = Template(template_name="index.html.jinja2", context=context)
    return index


#  @post("/webhook-github",  # this one is being used
#        include_in_schema=False,
#        **noauth,  # pyright: ignore
#        )
#  async def github_webhook_notify(request: Request, data: dict) -> str:
#      signature_header = request.headers.getone("X-Hub-Signature-256", "=")
#      data_bytes = await request.body()
#
#      if verify_github_webhook_signature(data_bytes=data_bytes,
#                                         webhook_secret=secret_config\
#                                                        .GITHUB_WEBHOOK_SECRET,
#                                         signature=signature_header):
#
#
#          ntfy_client(message=json.dumps(data), title="data dict",
#                      priority="default")
#
#          message = github_webhook_info_message(data=data)
#          ntfy_client(message=message, title="from /webhook-github",
#                      priority="default")
#
#          git_message = git_pull_repo(data)
#          if git_message:
#              ntfy_client(message=git_message, title="git pull 'repo'",
#                          priority="default")
#
#          return message
#
#      else:
#          message = "error checking"
#
#          ntfy_client(message=message, title="from /webhook-github",
#                      priority="high")
#
#          raise HTTPException(detail="Invalid signature",
#                  status_code=HTTP_403_FORBIDDEN)


@post("/webhook-github",
      include_in_schema=False,
      **noauth,  # pyright: ignore
      )
async def github_webhook(request: Request, data: dict) -> NoneType:
    # FIXME: later, change the endpoint to /webhook-github

    signature_header = request.headers.getone("X-Hub-Signature-256", "=")
    data_bytes = await request.body()

    repository_full_name = data["repository"]["full_name"]

    if not repository_full_name in WEBHOOK_DATA:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    else:
        repository_name = repository_full_name
        repository_local_directory = \
                WEBHOOK_DATA[repository_full_name]["local_directory"]
        repository_github_token = \
                WEBHOOK_DATA[repository_full_name]["github_token"]

        commit_message = data["head_commit"]["message"]

        user = secret_config.USER

    if not verify_github_signature(data_bytes=data_bytes,
                                   webhook_secret=repository_github_token,
                                   signature=signature_header):

        raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    ntfy_client(message="Webhook kicked in...",
                title=f"GitHub: {repository_name}")

    # repository is locally set
    # and signature is valid; continuing

    git_output = git_pull_repository(
            repository_local_directory=repository_local_directory,
            user=user,
            commit_message=commit_message,
            data=data)

    message = github_webhook_info_message(data=data)

    #  notification_lines = [git_output, "", "--- --- ---", "", "", message]
    notification_lines = [git_output, "--- --- ---", message]
    notification = "\n".join(notification_lines)

    if notification:
        ntfy_client(message=notification,
                    title=f"git pull '{repository_name}'")

    return None


@get("/reboot")
async def reboot() -> str:
    do_reboot()

    return ""


@get("/add_user")
async def user_add():
    pass

