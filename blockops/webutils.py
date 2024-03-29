from blockops.utils.params import Parameter as BlockParameter
from wepps.stage.parameters import Parameter as WebParameter

from wepps.stage import parameters as web_params
from blockops.utils import params as block_params

# Note: M = nPoints


def convert_to_web(params: dict[str, BlockParameter]) -> list[WebParameter]:
    web_parameters = []
    for param in params.values():
        # If its a MultipleChoices parameter, then separate the optional pTypes
        if isinstance(param, block_params.MultipleChoices):
            # TODO: Check if id is unique (and add a dependency?)
            for inner_param in param.pTypes:
                web_parameters.append(convert_block_param_to_web(inner_param))
        web_parameters.append(convert_block_param_to_web(param))
    return web_parameters


# Note that it converts the MultipleChoices to two different WebParameters
def convert_block_param_to_web(param: BlockParameter, name=None) -> WebParameter:
    id_name = str(param.uniqueID) if name is None else name
    name = param.latexName
    placeholder = str(param.__doc__)
    doc = str(param.docs).replace('\n', ' ')
    default = param.default
    if isinstance(param, block_params.PositiveInteger):
        if param.strict:
            return web_params.StrictlyPositiveInteger(id_name, name,
                                                      placeholder, doc, False,
                                                      default)
        return web_params.PositiveInteger(id_name, name, placeholder, doc, False,
                                          default)
    if isinstance(param, block_params.ScalarNumber):
        if param.positive:
            return web_params.PositiveFloat(id_name, name, placeholder, doc, False,
                                            default)
        return web_params.Float(id_name, name, placeholder, doc, False, default)
    if isinstance(param, block_params.VectorNumbers) or isinstance(
            param, block_params.CustomPoints):
        return web_params.FloatList(id_name, name, placeholder, doc,  False,default)
    if isinstance(param, block_params.Boolean):
        return web_params.Boolean(id_name, name, placeholder, doc,  False,default)
    if isinstance(param, block_params.MultipleChoices):
        if len(param.pTypes) > 0:
            raise NotImplementedError(
                'Yep... "MultipleChoices" currently not implemented')
        return web_params.Enumeration(id_name, name, placeholder, doc, False,
                                      param.choices, default)
    raise RuntimeError('Unknown WebType: {param}')
