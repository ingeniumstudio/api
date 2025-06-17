import os
import subprocess

from pathlib import Path

from litestar import Litestar
from litestar import MediaType
from litestar import Response
from litestar import get
from litestar import post
from litestar.datastructures import Headers

#  from litestar.params import Parameter
from litestar.logging import LoggingConfig

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.response import Template
from litestar.template.config import TemplateConfig

from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import RapidocRenderPlugin
from litestar.openapi.plugins import RedocRenderPlugin
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.openapi.plugins import StoplightRenderPlugin
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.openapi.plugins import YamlRenderPlugin

from functions import get_dhammapada
from functions import text_to_image
from functions import ntfy_client
from functions import box as box_function
from functions import cowsay as cowsay_function
from functions import fortune as fortune_function

import secret_config

#  from aux.operations import TextToImageOperation

from aux.params import parameter_optional_text
from aux.params import parameter_required_text
from aux.params import parameter_padding
from aux.params import parameter_foreground_color
from aux.params import parameter_background_color
from aux.params import parameter_font_size
from aux.params import parameter_box
from aux.params import parameter_cowsay
from aux.params import parameter_fortune

#  DEBUG = True
DEBUG = False

SQLITE_FILE_NAME = secret_config.SQLITE_FILE_NAME
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

@get("/",
     include_in_schema=False)
async def hello_world() -> dict[str, str]:
    """Handler function that returns a greeting dictionary."""
    return {"hello": "world!"}


@get("/display-dhammapada",
        media_type=MediaType.TEXT,
        summary="displays Dhammapada",
        description="Display a random verse from the Dhammapada if `number` is not specified, verse `number` otherwise",
        )
async def display_dhammapada(number: int | None = None,
                             format: str | None = None,
                             padding: parameter_padding = 22,
                             foreground_color: parameter_foreground_color = "white",
                             background_color: parameter_background_color = "black",
                             font_size: parameter_font_size = 16,
                             box: parameter_box = False
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


@get("/text-to-image")
async def text_to_img(
                      text: parameter_optional_text,
                      padding: parameter_padding = 0,
                      foreground_color: parameter_foreground_color = "white",
                      background_color: parameter_background_color = "black",
                      font_size: parameter_font_size = 16,
                      box: parameter_box = False,
                      cowsay: parameter_cowsay = False,
                      fortune: parameter_fortune = False,
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
     summary="cow sayin'",
     description="Cowsays `text`")
async def get_cowsay(text: parameter_required_text) -> str:
    cowsaying = cowsay_function(text=text)

    return cowsaying


@get("/box",
     media_type=MediaType.TEXT,
     summary="text inside box",
     description="Displays `text` inside box")
async def get_box(text: parameter_required_text) -> str:
    text_box = box_function(text=text)

    return text_box

@get("/fortune",
     media_type=MediaType.TEXT,
     summary="displays fortune",
     description="Displays a random fortune")
async def get_fortune() -> str:
    fortune_text = fortune_function()

    return fortune_text

@post("/webhook-github",
      include_in_schema=False)
async def github_webhook_notify(data: dict) -> dict:
    ntfy_client(message=str(data),
                title="from /webhook-github",
                priority="high")

    return data

route_handlers = [
        hello_world,
        display_dhammapada,
        text_to_img,
        get_cowsay,
        get_box,
        get_fortune,
        github_webhook_notify,
        ]

logging_config = LoggingConfig(
        root={
            "level": "INFO",
            "handlers": ["queue_listener"]
            },
        formatters={
            "standard": { "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s" }
            },
        log_exceptions="always"
        )

template_config = TemplateConfig(directory=Path(__file__) / "templates",
                                 engine=JinjaTemplateEngine)

# https://docs.litestar.dev/2/usage/openapi/schema_generation.html
# https://docs.litestar.dev/2/reference/app.html

app = Litestar(route_handlers=route_handlers,
               logging_config=logging_config,
               template_config=template_config,
               openapi_config=OpenAPIConfig(
                   title='Yoke API',
                   version='0.0.1',
                   use_handler_docstrings=False,
                   render_plugins=[
                       RapidocRenderPlugin(),
                       RedocRenderPlugin(),
                       ScalarRenderPlugin(),
                       StoplightRenderPlugin(),
                       SwaggerRenderPlugin(),
                       YamlRenderPlugin()
                       ],
                   ),
               pdb_on_exception=DEBUG
               )
