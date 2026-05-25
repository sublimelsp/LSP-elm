from __future__ import annotations

from LSP.protocol import DocumentUri
from LSP.protocol import Range
from LSP.protocol import TextDocumentIdentifier
from typing import TypedDict
from typing_extensions import NotRequired


class MoveDestination(TypedDict):
    name: str
    path: str
    uri: str


class MoveParamsParams(TypedDict):
    textDocument: TextDocumentIdentifier
    range: Range


class MoveParams(TypedDict):
    sourceUri: DocumentUri
    params: MoveParamsParams
    destination: NotRequired[MoveDestination]


class MoveDestinationsResponse(TypedDict):
    destinations: list[MoveDestination]


class MoveFunctionCommand(TypedDict):
    arguments: tuple[str, MoveParamsParams, str]
    command: str  # string like elm.refactor-${workspaceId}, for example: 'elm.refactor-file:///home/predragnikolic/Documents/sandbox/elm-spa-example'
    title: str
