from pathlib import Path
from re import template
from typing import IO

from litestar import Litestar
from litestar import Response
from litestar import get
from litestar.datastructures import Headers

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.response import Template
from litestar.template.config import TemplateConfig


from functions import get_dhammapada
from functions import text_to_image

#  class InMemoryFileResponse(Response[bytes]):
#      def __init__(self, buf: IO, name: str):
#          super().__init__(buf.getvalue(), headers={"content-disposition": f"attachment;filename={name}")

# https://caddyserver.com/docs/quick-starts/reverse-proxy

# https://docs.litestar.dev/latest/

# sudo caddy reverse-proxy --from sub.kassius.org --to :8000
# $ litestar run

# https://docs.litestar.dev/2/topics/deployment/supervisor.html#alternatives

# https://docs.litestar.dev/2/usage/templating.html#template-responses

# https://github.com/Tobi-De/litestar-browser-reload

# https://stackoverflow.com/questions/55873174/how-do-i-return-an-image-in-fastapi

# https://github.com/orgs/litestar-org/discussions/1868

@get("/")
async def hello_world() -> dict[str, str]:
    """Handler function that returns a greeting dictionary."""
    return {"hello": "world!"}


@get("/display-dhammapada")
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
               template_config=template_config)
