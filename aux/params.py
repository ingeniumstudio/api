from typing import Annotated
from typing import Literal

from litestar.params import Parameter

# https://docs.litestar.dev/latest/reference/params.html#litestar.params.Parameter
param_optional_text = Annotated[str | None,
                                    Parameter(
                                        description="Input text",
                                        min_length=0,
                                        max_length=8192
                                    )]

param_required_text = Annotated[str,
                                    Parameter(
                                        description="Input text",
                                        min_length=0,
                                        max_length=8192
                                    )]

param_padding = Annotated[int,
                              Parameter(
                                  description="Inner padding",
                                  ge=0,
                                  le=1024
                              )]

param_space_padding = Annotated[bool,
                          Parameter(
                              description="Makes all lines the same lenght by adding spaces after text",
                          )]

#  param_foreground_color = Annotated[str | None,
param_foreground_color = Annotated[str,
                                       Parameter(
                                           description="**Foreground color**",
                                           min_length=0,
                                           max_length=32
                                       )]

#  param_background_color = Annotated[str | None,
param_background_color = Annotated[str,
                                       Parameter(
                                           description="Background color",
                                           min_length=0,
                                           max_length=32
                                       )]

param_font_size = Annotated[int,
                                Parameter(
                                    description="Font size",
                                    ge=5,
                                    le=288
                                )]

param_box = Annotated[bool,
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


param_cowsay = Annotated[bool,
                             Parameter(
                                 description=param_description_cowsay,
                             )]

param_fortune = Annotated[bool,
                              Parameter(
                                  description="Show random fortune; input "
                                              "`text` is ignored if `true`",
                              )]

param_dhammapada_number = Annotated[int | None,
                                        Parameter(
                                            description="Dhammapada "
                                                        "verse number",
                                            ge=1,
                                            le=423
                                        )]

dhammapada_formats = Literal["txt", "png"]
param_dhammapada_format = Annotated[dhammapada_formats | None,
                                        Parameter(
                                            description="Output format; `png`"
                                                        " for `image/png` or"
                                                        " empty for"
                                                        " `text/plain`",
                                        )]
