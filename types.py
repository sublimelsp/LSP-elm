from typing_extensions import NotRequired, TypedDict, List, Tuple
from LSP.plugin.core.protocol import URI, Location, Range, TextDocumentIdentifier

# Code Lens Show Reference - Start
class ShowReference(TypedDict):
    references: List[Location]
    uri: URI
    range: Range

ShowReferencesParams = List[ShowReference]
# Code Lens Show Reference - End

# Move Function Code Action - Start
class MoveDestination(TypedDict):
    name: str
    path: str
    uri: str


class MoveParamsParams(TypedDict):
    textDocument: TextDocumentIdentifier
    range: Range


class MoveParams(TypedDict):
    sourceUri: URI
    params: MoveParamsParams
    destination: NotRequired[MoveDestination]


class MoveDestinationsResponse(TypedDict):
    destinations: List[MoveDestination]


class MoveFunctionCommand(TypedDict):
    arguments: Tuple[str, MoveParamsParams, str]
    command: str  # string like elm.refactor-${workspaceId}, for example: 'elm.refactor-file:///home/predragnikolic/Documents/sandbox/elm-spa-example'
    title: str
# Move Function Code Action - End
