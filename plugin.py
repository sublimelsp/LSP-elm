from __future__ import annotations

from .types import MoveDestinationsResponse
from .types import MoveFunctionCommand
from .types import MoveParams
from .types import MoveParamsParams
from LSP.plugin import Error
from LSP.plugin import LspPlugin
from LSP.plugin import OnPreStartContext
from LSP.plugin import Request
from LSP.plugin import ServerResponse
from LSP.plugin import Session
from LSP.protocol import CodeAction
from lsp_utils import NodeManager
from pathlib import Path
from sublime_lib import ResourcePath
from typing import cast
from typing_extensions import override
import sublime


def plugin_loaded():
    LspElmPlugin.register()


def plugin_unloaded():
    LspElmPlugin.unregister()


class LspElmPlugin(LspPlugin):

    @classmethod
    @override
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        package_name = cls.plugin_storage_path.name
        NodeManager.on_pre_start_async(
            context,
            cls.plugin_storage_path,
            ResourcePath('Packages', package_name, 'server'),
            Path('node_modules', '@elm-tooling', 'elm-language-server', 'out', 'node', 'index.js'),
            node_version_requirement='>=14',
        )

    @override
    def on_server_response_async(self, response: ServerResponse) -> None:
        if response['method'] == 'codeAction/resolve' and (session := self.weaksession()):
            code_action = response['result']
            if code_action['title'] != 'Move Function':
                self.handle_move_code_action(session, code_action)

    def handle_move_code_action(self, session: Session, code_action: CodeAction) -> None:
        command = cast(MoveFunctionCommand, code_action.get('command'))
        if not command:
            return
        _, params, function_name = command.get('arguments')
        move_params: MoveParams = {
            'sourceUri': params.get('textDocument').get('uri'),
            'params': params
        }
        session.send_request_task(Request('elm/getMoveDestinations', move_params)) \
            .then(lambda result: self.on_get_destinations(result, params, function_name))

    def on_get_destinations(
        self, response: MoveDestinationsResponse | Error, params: MoveParamsParams, function_name: str
    ) -> None:
        if isinstance(response, Error):
            return
        destinations = response.get('destinations')
        if not destinations:
            sublime.status_message('LSP-elm: No destinations to choose.')
        session = self.weaksession()
        if not session:
            return
        window = sublime.active_window()
        if not window:
            return

        def on_done(index: int) -> None:
            if index == -1:
                return
            destination = destinations[index]
            move_params: MoveParams = {
                'sourceUri': params.get('textDocument').get('uri'),
                'params': params,
                'destination': destination
            }
            session.send_request_task(Request("elm/move", move_params))  # no need to handle result

        placeholder = f'Select the new file for the function {function_name}'
        items = [d['name'] for d in destinations]
        window.show_quick_panel(items, placeholder=placeholder, on_select=on_done)
