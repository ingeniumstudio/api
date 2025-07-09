from pathlib import Path

from litestar import Litestar

from litestar.middleware import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
    DefineMiddleware,
)

from litestar.connection import ASGIConnection

from litestar.exceptions import NotAuthorizedException

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig

from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import (
    RapidocRenderPlugin,
	RedocRenderPlugin,
	ScalarRenderPlugin,
	StoplightRenderPlugin,
	SwaggerRenderPlugin,
	YamlRenderPlugin,
)

from functions import ntfy_client
from functions import fortune as fortune_function
from functions import get_pids_in_port

from aux.logging import logging_config

from database import create_db_tables
from database import Text

from routes import (
    hello_world,
    display_dhammapada,
    text_to_img,
    get_cowsay,
    get_box,
    get_fortune,
    get_specific,
    get_index,
    github_webhook_notify,
    reboot,
)

import secret_config

#  DEBUG = True
DEBUG = False

noauth = {"exclude_from_auth": True}


class YokeAuthMiddleware(AbstractAuthenticationMiddleware):
    async def authenticate_request(self, connection: ASGIConnection)\
                  -> AuthenticationResult:

        auth_header = connection.headers.get(secret_config.API_KEY_HEADER)
        if not auth_header:
            raise NotAuthorizedException()

        auth = secret_config.check_auth(header=auth_header)

        if not auth:
            raise NotAuthorizedException()

        return AuthenticationResult(**auth)


async def on_startup():
    await create_db_tables(Text, if_not_exists=True)

    fortune = fortune_function()
    await Text.insert(Text(text=fortune))

    pid_list = get_pids_in_port(port=8000)
    message = f"pids: {', '.join(pid_list)}\n\n{fortune}"
    ntfy_client(message=message, title="server started", priority="low")


async def on_shutdown():
    texts = await Text.select()
    fortune = "\n\n".join([f"{text['id']}: {text['text']}"
                                 for text in texts])

    pid_list = get_pids_in_port(port=8000)
    message = f"pids: {', '.join(pid_list)}\n\n{fortune}"
    ntfy_client(message=message, title="server stopping", priority="low")

auth_mw = DefineMiddleware(YokeAuthMiddleware, exclude="schema")

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
        reboot,
        ]

template_config = TemplateConfig(directory=Path("templates"),
        engine=JinjaTemplateEngine)

# https://docs.litestar.dev/2/usage/openapi/schema_generation.html
# https://docs.litestar.dev/2/reference/app.html

app = Litestar(route_handlers=route_handlers,
               middleware=[auth_mw],
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
               on_startup=[on_startup],
               on_shutdown=[on_shutdown],
               pdb_on_exception=DEBUG
               )
