import os
import subprocess

from pathlib import Path
from re import template
from typing import IO
from typing import Annotated

from attr import dataclass
from litestar import Litestar
from litestar import MediaType
from litestar import Response
from litestar import get
from litestar import post
from litestar.datastructures import Headers

from litestar.params import Parameter
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

from litestar.openapi.spec import Example
from litestar.openapi.spec import OpenAPIMediaType
from litestar.openapi.spec import OpenAPIType
from litestar.openapi.spec import Operation
from litestar.openapi.spec import Parameter as OASParameter
from litestar.openapi.spec import RequestBody
from litestar.openapi.spec import Schema

from functions import get_dhammapada
from functions import text_to_image
from functions import ntfy_client
from functions import box as box_function
from functions import cowsay as cowsay_function
from functions import fortune as fortune_function

#  DEBUG = True
DEBUG = False

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


#  @dataclass
class TextToImageOperation(Operation):
    #  summary = "summ"
    #  description = "test"

    def __init__(self, *args, **kwargs) -> None:
        self.summary = "summry"
        self.description = "teste"
        #  self.parameters = [
        #          OASParameter(name="text", param_in="query", description="he ya", example="oie")
        #
        #          ]

#  async def text_to_img(text: str | None = Parameter(description="descr1pt1onz",
#      title="Teh Text", examples=[Example(summary="hett", description="* descc", value="WOT")]),
@get("/text-to-image")
async def text_to_img(text: str | None,
                      padding: int = 0,
                      foreground_color: str = "white",
                      background_color: str = "black",
                      font_size: int = 16,
                      box: bool = False,
                      cowsay: bool = False,
                      fortune: bool = False
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
async def get_cowsay(text: str) -> str:
    cowsaying = cowsay_function(text=text)

    return cowsaying


@get("/box",
        media_type=MediaType.TEXT,
        summary="text inside box",
        description="Displays `text` inside box")
async def get_box(text: str) -> str:
    text_box = box_function(text=text)

    return text_box


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
                       ]
                   ),
               pdb_on_exception=DEBUG
               )
