import shutil
import os
import sublime

from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.settings import ClientConfig, read_client_config

from lsp_utils import ServerNpmResource

PACKAGE_NAME = 'LSP-elm'
SETTINGS_FILENAME = 'LSP-elm.sublime-settings'
SERVER_DIRECTORY = 'server'
SERVER_BINARY_PATH = os.path.join(SERVER_DIRECTORY, 'node_modules', '@elm-tooling', 'elm-language-server', 'out', 'index.js')

server = ServerNpmResource(PACKAGE_NAME, SERVER_DIRECTORY, SERVER_BINARY_PATH)


def plugin_loaded():
    server.setup()


def plugin_unloaded():
    server.cleanup()


def is_node_installed():
    return shutil.which('node') is not None


class LspElmPlugin(LanguageHandler):
    @property
    def name(self) -> str:
        return PACKAGE_NAME.lower()

    @property
    def config(self) -> ClientConfig:
        # Calling setup() also here as this might run before `plugin_loaded`.
        # Will be a no-op if already ran.
        # See https://github.com/sublimelsp/LSP/issues/899
        server.setup()

        settings = sublime.load_settings(SETTINGS_FILENAME)

        configuration = {
            "enabled": settings.get("enabled", True),
            "command": ['node', server.binary_path, '--stdio'],
            "languages": settings.get("languages"),
            "initializationOptions": settings.get("initializationOptions"),
            "settings": settings.get("settings")
        }

        return read_client_config(self.name, configuration)

    def on_start(self, window) -> bool:
        if not is_node_installed():
            sublime.status_message("{}: Please install Node.js for the server to work.".format(PACKAGE_NAME))
            return False
        return server.ready

    def on_initialized(self, client) -> None:
        pass   # extra initialization here.
