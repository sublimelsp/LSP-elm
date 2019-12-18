import sublime
import sublime_plugin

from LSP.plugin.core.protocol import Request, Range
from LSP.plugin.core.settings import settings, client_configs
from LSP.plugin.core.url import filename_to_uri
from LSP.plugin.core.registry import session_for_view, sessions_for_view, client_from_session, configs_for_scope
from LSP.plugin.core.views import range_to_region
from LSP.plugin.core.configurations import is_supported_syntax
from LSP.plugin.core.documents import is_transient_view


try:
    from typing import Any, List, Dict, Callable, Optional
    assert Any and List and Dict and Callable and Optional
except ImportError:
    pass


color_phantoms_by_view = dict()  # type: Dict[int, sublime.PhantomSet]


class LspCodeLensListener(sublime_plugin.ViewEventListener):
    def __init__(self, view: sublime.View) -> None:
        super().__init__(view)
        self._stored_point = -1
        self.initialized = False
        self.enabled = False
        self.phantoms = []
        self.phantom_set = sublime.PhantomSet(self.view, 'code_lens')

    @classmethod
    def is_applicable(cls, _settings: 'Any') -> bool:
        syntax = _settings.get('syntax')
        is_supported = syntax and is_supported_syntax(syntax, client_configs.all)
        disabled_by_user = 'codeLensProvider' in settings.disabled_capabilities
        return is_supported and not disabled_by_user

    def on_activated_async(self) -> None:
        if not self.initialized:
            self.initialize()

    def initialize(self, is_retry: bool = False) -> None:
        configs = configs_for_scope(self.view)
        if not configs:
            self.initialized = True  # no server enabled, re-open file to activate feature.
        sessions = list(sessions_for_view(self.view))
        if sessions:
            self.initialized = True
            if any(session.has_capability('codeLensProvider') for session in sessions):
                self.enabled = True
                self.send_code_lens_request()
        elif not is_retry:
            # session may be starting, try again once in a second.
            sublime.set_timeout_async(lambda: self.initialize(is_retry=True), 1000)
        else:
            self.initialized = True  # we retried but still no session available.

    def on_modified_async(self) -> None:
        if self.enabled:
            self.schedule_request()

    def schedule_request(self) -> None:
        sel = self.view.sel()
        if len(sel) < 1:
            return

        current_point = sel[0].begin()
        if self._stored_point != current_point:
            self._stored_point = current_point
            sublime.set_timeout_async(lambda: self.fire_request(current_point), 800)

    def fire_request(self, current_point: int) -> None:
        if current_point == self._stored_point:
            self.send_code_lens_request()

    def send_code_lens_request(self) -> None:
        if is_transient_view(self.view):
            return

        client = client_from_session(session_for_view(self.view, 'codeLensProvider'))
        if client:
            file_path = self.view.file_name()
            if file_path:
                params = {
                    "textDocument": {
                        "uri": filename_to_uri(file_path)
                    }
                }
                client.send_request(
                    Request.codeLens(params),
                    self.handle_response
                )

    def handle_response(self, code_lens_response: 'Optional[List[dict]]') -> None:
        client = client_from_session(session_for_view(self.view, 'codeLensProvider'))
        if client and code_lens_response:
            for code_lens in code_lens_response:
                client.send_request(
                    Request.codeLensResolve(code_lens),
                    self.handle_resolve
                )

    def handle_resolve(self, response: 'Optional[List[dict]]') -> None:
        range = Range.from_lsp(response['range'])
        region = range_to_region(range, self.view)

        content = "<small>{}</small>".format(response["command"]["title"])
        for p in self.phantoms:
            if p.region.contains(region):
                content = "{} | {}".format(p.content, content)
                self.phantoms.remove(p)

        self.phantoms.append(sublime.Phantom(region, content, sublime.LAYOUT_BELOW))
        self.phantom_set.update(self.phantoms)
