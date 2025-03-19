from pathlib import Path
from re import template
from typing import IO

from litestar import Litestar
from litestar import MediaType
from litestar import Response
from litestar import get
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


@get("/")
async def hello_world() -> dict[str, str]:
    """Handler function that returns a greeting dictionary."""
    return {"hello": "world!"}


@get("/display-dhammapada", media_type=MediaType.TEXT)
async def display_dhammapada(number: int | None = None,
                             format: str | None = None) -> str | Response:
    dhammapada = get_dhammapada(number=number)

    if format == "png":
        png_bytes = text_to_image(text=dhammapada)

        return Response(
            content=png_bytes,
            media_type="image/png",
            headers=Headers({"Content-Disposition": "inline; filename=image.png"})
        )

    return dhammapada


@get("/img")
async def text_to_img(text: str) -> Response:
    png_bytes = text_to_image(text=text)

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers=Headers({"Content-Disposition": "inline; filename=image.png"})
    )


route_handlers = [
        hello_world,
        display_dhammapada,
        text_to_img
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
                   )
               )
