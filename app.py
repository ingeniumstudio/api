from typing import IO

from litestar import Litestar
from litestar import Response
from litestar import get
from litestar.datastructures import Headers

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


@get("/img")
async def text_to_img(text: str) -> Response:

    png_bytes = text_to_image(text=text)

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers=Headers({"Content-Disposition": "inline; filename=example.png"})
    )

app = Litestar(route_handlers=[hello_world, text_to_img])
