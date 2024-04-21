from __future__ import annotations
from typing_extensions import TypeAlias, NotRequired, TypedDict
from LSP.plugin.core.protocol import URI, Location, Range, TextDocumentIdentifier

# Code Lens Show Reference - Start
class ShowReference(TypedDict):
    references: list[Location]
    uri: URI
    range: Range

ShowReferencesParams: TypeAlias = 'list[ShowReference]'
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
    destinations: list[MoveDestination]


class MoveFunctionCommand(TypedDict):
    arguments: tuple[str, MoveParamsParams, str]
    command: str  # string like elm.refactor-${workspaceId}, for example: 'elm.refactor-file:///home/predragnikolic/Documents/sandbox/elm-spa-example'
    title: str
# Move Function Code Action - End
