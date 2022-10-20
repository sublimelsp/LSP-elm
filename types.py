from LSP.plugin.core.protocol import URI, CodeActionParams, Location, NotRequired, Range, TextDocumentIdentifier
from LSP.plugin.core.typing import Tuple, TypedDict, List

# Code Lens Show Reference - Start
ShowReference = TypedDict('ShowReference', {
    'references': List[Location],
    'uri': URI,
    'range': Range
})

ShowReferencesParams = List[ShowReference]
# Code Lens Show Reference - End

# Move Function Code Action - Start
MoveDestination = TypedDict('MoveDestination', {
  'name': str,
  'path': str,
  'uri': str
})

MoveParamsParams = TypedDict('MoveFunctionCodeActionArgument', {
    'textDocument': TextDocumentIdentifier,
    'range': Range
})

MoveParams = TypedDict('MoveParams', {
  'sourceUri': URI,
  'params': MoveParamsParams,
  'destination': NotRequired[MoveDestination]
})

MoveDestinationsResponse = TypedDict('MoveDestinationsResponse', {
  'destinations': List[MoveDestination]
})

MoveFunctionCodeAction = TypedDict("MoveFunctionCodeAction", {
  'arguments': Tuple[str, MoveParamsParams, str],
  'command': str,  # string like elm.refactor-${workspaceId}, for example: 'elm.refactor-file:///home/predragnikolic/Documents/sandbox/elm-spa-example'
  'title': str
})

MaybeMoveFunctionCodeAction = TypedDict("MaybeMoveFunctionCodeAction", {
  'command': NotRequired[MoveFunctionCodeAction]
  # other properties are not important for the move request
})
# Move Function Code Action - End


