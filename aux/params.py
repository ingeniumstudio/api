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

cowsay_sample = """

```
 _______
< hello >
 -------
        \\   ^__^
         \\  (oo)\\_______
            (__)\\       )\\/\\
                ||----w |
                ||     ||
```
"""

param_description_cowsay = """
Cowsay input `text`
"""


parameter_cowsay = Annotated[bool,
                             Parameter(
                                 description=param_description_cowsay,
                             )]

parameter_fortune = Annotated[bool,
                              Parameter(
                                  description="Show random fortune; input "
                                              "`text` is ignored if `true`",
                              )]

parameter_dhammapada_number = Annotated[int | None,
                                        Parameter(
                                            description="Dhammapada "
                                                        "verse number",
                                            ge=1,
                                            le=423
                                        )]

parameter_dhammapada_format = Annotated[str | None,
                                        Parameter(
                                            description="Output format; `png`"
                                                        " for `image/png` or"
                                                        " empty for"
                                                        " `text/plain`",
                                            min_length=0,
                                            max_length=11
                                        )]
