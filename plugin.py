import os
from lsp_utils import NpmClientHandler


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
    def install_in_cache(cls) -> bool:
        return False
