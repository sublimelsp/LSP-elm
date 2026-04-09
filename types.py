from __future__ import annotations

from LSP.protocol import Location
from LSP.protocol import Range
from LSP.protocol import TextDocumentIdentifier
from LSP.protocol import URI
from typing import List
from typing import TypedDict
from typing_extensions import NotRequired


# Code Lens Show Reference - Start
class ShowReference(TypedDict):
    references: list[Location]
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
    destinations: list[MoveDestination]


class MoveFunctionCommand(TypedDict):
    arguments: tuple[str, MoveParamsParams, str]
    command: str  # string like elm.refactor-${workspaceId}, for example: 'elm.refactor-file:///home/predragnikolic/Documents/sandbox/elm-spa-example'
    title: str
# Move Function Code Action - End
