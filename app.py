import os
import subprocess

from pathlib import Path
from re import template
from typing import IO

from litestar import Litestar
from litestar import MediaType
from litestar import Response
from litestar import get
from litestar import post
from litestar.datastructures import Headers

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

#  DEBUG = True
DEBUG = False

@get("/")
async def hello_world() -> dict[str, str]:
    """Handler function that returns a greeting dictionary."""
    return {"hello": "world!"}


@get("/display-dhammapada", media_type=MediaType.TEXT)
async def display_dhammapada(number: int | None = None,
                             format: str | None = None,
                             padding: int = 22,
                             foreground_color: str = "white",
                             background_color: str = "black",
                             font_size: int = 16,
                             box: bool = False
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
async def text_to_img(text: str | None = None,
                      padding: int = 0,
                      foreground_color: str = "white",
                      background_color: str = "black",
                      font_size: int = 16,
                      box: bool = False,
                      cowsay: bool = False,
                      fortune: bool = False
                      ) -> Response:

    if fortune or not text:
        text = fortune_function(text=text)

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

@post("/webhook-github")
async def github_webhook_notify(data: dict) -> dict:
    ntfy_client(message=str(data),
                title="from /webhook-github",
                priority="high")

    return data

route_handlers = [
        hello_world,
        display_dhammapada,
        text_to_img,
        github_webhook_notify,
        ]

template_config = TemplateConfig(directory=Path(__file__) / "templates",
                                 engine=JinjaTemplateEngine)

app = Litestar(route_handlers=route_handlers,
               template_config=template_config,
               openapi_config=OpenAPIConfig(
                   title='Yoke API',
                   version='0.0.1',
                   render_plugins=[
                       RapidocRenderPlugin(),
                       RedocRenderPlugin(),
                       ScalarRenderPlugin(),
                       StoplightRenderPlugin(),
                       SwaggerRenderPlugin(),
                       YamlRenderPlugin()
                       ]
                   ),
               pdb_on_exception=DEBUG
               )
