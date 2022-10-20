from .types import ShowReferencesParams
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
        server_directory, 'node_modules', '@elm-tooling', 'elm-language-server', 'out', 'index.js'
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



