from litestar.openapi.spec import Example
from litestar.openapi.spec import OpenAPIMediaType
from litestar.openapi.spec import OpenAPIType
from litestar.openapi.spec import Operation
from litestar.openapi.spec import Parameter as OASParameter
from litestar.openapi.spec import RequestBody
from litestar.openapi.spec import Schema

#  ┌──────────────┐
#  │ YET NOT USED │
#  └──────────────┘


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
