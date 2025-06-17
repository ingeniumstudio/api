from typing import Annotated

from litestar.params import Parameter

# https://docs.litestar.dev/latest/reference/params.html#litestar.params.Parameter
parameter_optional_text = Annotated[str | None,
                                    Parameter(
                                        description="Input text",
                                        min_length=0,
                                        max_length=8192
                                    )]

parameter_required_text = Annotated[str,
                                    Parameter(
                                        description="Input text",
                                        min_length=0,
                                        max_length=8192
                                    )]

parameter_padding = Annotated[int,
                              Parameter(
                                  description="Inner padding",
                                  ge=0,
                                  le=1024
                              )]

parameter_foreground_color = Annotated[str | None,
                                       Parameter(
                                           description="**Foreground color**",
                                           min_length=0,
                                           max_length=32
                                       )]

parameter_background_color = Annotated[str | None,
                                       Parameter(
                                           description="Background color",
                                           min_length=0,
                                           max_length=32
                                       )]

parameter_font_size = Annotated[int,
                                Parameter(
                                    description="Font size",
                                    ge=5,
                                    le=288
                                )]

parameter_box = Annotated[bool,
                          Parameter(
                              description="Bounding box",
                          )]

parameter_cowsay = Annotated[bool,
                             Parameter(
                                 description="Cowsay input `text`",
                             )]

parameter_fortune = Annotated[bool,
                              Parameter(
                                  description="Show random fortune; input `text` is ignored if `true`",
                              )]
