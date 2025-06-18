import os
import subprocess

from pathlib import Path

from typing import Optional

from litestar import Litestar
from litestar import MediaType
from litestar import Response
from litestar import Request
from litestar import get
from litestar import post
from litestar.datastructures import Headers

from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN

from litestar.logging import LoggingConfig

from litestar.contrib.jinja import JinjaTemplateEngine
#  from litestar.contrib.mako import MakoTemplateEngine
from litestar.response import Template
from litestar.template.config import TemplateConfig

from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import RapidocRenderPlugin
from litestar.openapi.plugins import RedocRenderPlugin
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.openapi.plugins import StoplightRenderPlugin
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.openapi.plugins import YamlRenderPlugin

from sqlmodel import Field
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel import select

from functions import get_dhammapada
from functions import text_to_image
from functions import ntfy_client
from functions import box as box_function
from functions import cowsay as cowsay_function
from functions import fortune as fortune_function
from functions import verify_github_webhook_signature
from functions import process_github_webhook

import secret_config

from aux.logging import logging_config

#  from aux.operations import TextToImageOperation

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

#  DEBUG = True
DEBUG = False

#  DB_FILE_DELETE_IF_EXISTS = True  # recreate db file
DB_FILE_DELETE_IF_EXISTS = False  # recreate db file
#  DB_IN_MEMORY = True
DB_IN_MEMORY = False

if DB_IN_MEMORY:
    SQLITE_URL = f"sqlite://"  # in-memory
else:
    SQLITE_FILE_NAME = secret_config.SQLITE_FILE_NAME
    SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

    if DB_FILE_DELETE_IF_EXISTS and os.path.isfile(SQLITE_FILE_NAME):
        os.remove(SQLITE_FILE_NAME)

class Text(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str

engine = create_engine(url=SQLITE_URL, echo=True)

SQLModel.metadata.create_all(engine)

session = Session(bind=engine)
text1 = Text(text=fortune_function())
session.add(text1)
session.commit()
session.close()

@get("/", include_in_schema=False)
async def hello_world() -> dict[str, str]:
    """Handler function that returns a greeting dictionary."""
    return {"hello": "world!"}


@get("/display-dhammapada",
        media_type=MediaType.TEXT,
        summary="displays dhammapada",
        description="Display a random verse from the Dhammapada if `number` is not specified, verse `number` otherwise",
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
        description="Generates an image from `text`.")
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
     description="Cowsays `text`")
async def get_cowsay(text: param_required_text) -> str:
    cowsaying = cowsay_function(text=text)

    return cowsaying


@get("/box",
     media_type=MediaType.TEXT,
     summary="text inside box",
     description="Displays `text` inside box")
async def get_box(text: param_required_text) -> str:
    text_box = box_function(text=text)

    return text_box


@get("/fortune",
     media_type=MediaType.TEXT,
     summary="displays fortune",
     description="Displays a random fortune")
async def get_fortune() -> str:
    fortune_text = fortune_function()

    return fortune_text


@get("/specific",
     media_type=MediaType.TEXT,
     summary="displays specific fortune",
     description="Displays a chosen fortune")
async def get_specific() -> str:
    session = Session(bind=engine)

    statement = select(Text)
    results = session.exec(statement)

    specific_text = "\n\n".join([f"{result.id}: {result.text}"
                               for result in results])

    session.close()

    return specific_text


@get("/index",
     media_type=MediaType.HTML,
     summary="template",
     description="Testing templates")
async def get_index(text: param_required_text) -> str:
    context = {"text": text}

    index = Template(template_name="index.html.jinja2", context=context)
    return index


@post("/webhook-github", include_in_schema=False)
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
                    priority="high")

        return message

    else:
        message = "error checking"

        ntfy_client(message=message, title="from /webhook-github",
                    priority="high")

        raise HTTPException(detail="Invalid signature",
                status_code=HTTP_403_FORBIDDEN)



route_handlers = [
        hello_world,
        display_dhammapada,
        text_to_img,
        get_cowsay,
        get_box,
        get_fortune,
        get_specific,
        get_index,
        github_webhook_notify,
        ]

print(Path(__file__))
template_config = TemplateConfig(directory=Path("templates"),
        engine=JinjaTemplateEngine)
                                 #  engine=JinjaTemplateEngine)

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
