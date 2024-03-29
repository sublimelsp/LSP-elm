from .types import MoveDestinationsResponse, MoveFunctionCommand, MoveParamsParams, ShowReferencesParams, MoveParams
from LSP.plugin.core.protocol import CodeAction, Request, Response
from LSP.plugin.core.typing import Mapping, Callable, Any, cast
from LSP.plugin.locationpicker import LocationPicker
from lsp_utils import NpmClientHandler
import os
import sublime


def plugin_loaded():
    LspElmPlugin.setup()


def plugin_unloaded():
    LspElmPlugin.cleanup()


class LspElmPlugin(NpmClientHandler):
    package_name = __package__
    server_directory = 'server'
    server_binary_path = os.path.join(
        server_directory, 'node_modules', '@elm-tooling', 'elm-language-server', 'out', 'node', 'index.js'
    )

    @classmethod
    def required_node_version(cls) -> str:
        return ">=14"

    def on_pre_server_command(self, params: Mapping[str, Any], done_callback: Callable[[], None]) -> bool:
        if params['command'] == 'editor.action.showReferences':
            arguments = cast(ShowReferencesParams, params['arguments'])
            session = self.weaksession()
            view = sublime.active_window().active_view()
            if not session or not view:
                done_callback()
                return True
            references = arguments[0]['references']
            if len(references) == 1:
                args = {
                    'location': references[0],
                    'session_name': session.config.name,
                }
                view.run_command('lsp_open_location', args)
            elif references:
                LocationPicker(view, session, references, side_by_side=False)
            else:
                sublime.status_message('No references found')
            done_callback()
        return True

    def on_server_response_async(self, method: str, response: Response) -> None:
        if method == 'codeAction/resolve':
            self.maybe_handle_move_code_action(cast(CodeAction, response.result))

    def maybe_handle_move_code_action(self, code_action: CodeAction) -> None:
        if code_action['title'] != 'Move Function':
            return
        session = self.weaksession()
        if not session:
            return
        command = cast(MoveFunctionCommand, code_action.get('command'))
        if not command:
            return
        _, params, function_name = command.get('arguments')
        move_params = {
            'sourceUri': params.get('textDocument').get('uri'),
            'params': params
        }  # type: MoveParams
        session.send_request(Request('elm/getMoveDestinations', move_params),
                             lambda res: self.on_get_destinations(res, params, function_name))

    def on_get_destinations(
        self, response: MoveDestinationsResponse, params: MoveParamsParams, function_name: str
    ) -> None:
        destinations = response.get('destinations')
        if not destinations:
            sublime.status_message('LSP-elm: No destinations to choose.')
        session = self.weaksession()
        if not session:
            return
        window = sublime.active_window()
        if not window:
            return

        def on_done(index) -> None:
            if index == -1:
                return
            destination = destinations[index]
            move_params = {
                'sourceUri': params.get('textDocument').get('uri'),
                'params': params,
                'destination': destination
            }  # type: MoveParams
            session.send_request(Request("elm/move", move_params),
                                 lambda _: None)  # no need to handle result

        placeholder = 'Select the new file for the function {}'.format(function_name)
        items = [d['name'] for d in destinations]
        window.show_quick_panel(items, placeholder=placeholder, on_select=on_done)
