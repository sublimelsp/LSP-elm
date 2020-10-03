import sublime
import sublime_plugin

from LSP.plugin.core.protocol import Request, Range
from LSP.plugin.core.settings import client_configs
from LSP.plugin.core.url import filename_to_uri
from LSP.plugin.core.registry import sessions_for_view, Session
from LSP.plugin.core.views import range_to_region
from LSP.plugin.core.views import range_to_region
from LSP.plugin.documents import is_transient_view
from LSP.plugin.core.typing import Generator


try:
    from typing import Any, List, Dict, Callable, Optional, Iterable
    assert Any and List and Dict and Callable and Optional and Iterable
except ImportError:
    pass


color_phantoms_by_view = dict()  # type: Dict[int, sublime.PhantomSet]


def find_session(view: sublime.View, capability: str, point: 'Optional[int]' = None) -> 'Optional[Session]':
    return _best_session(view, _sessions(view, capability), point)

def _best_session(view: sublime.View, sessions: 'Iterable[Session]', point: 'Optional[int]' = None) -> 'Optional[Session]':
    if point is None:
        try:
            point = view.sel()[0].b
        except IndexError:
            return None
    scope = view.scope_name(point)
    try:
        return max(sessions, key=lambda session: session.config.score_feature(scope))
    except ValueError:
        return None

def _sessions(view: sublime.View, capability: 'Optional[str]' = None) -> 'Generator[Session, None, None]':
    yield from sessions_for_view(view, capability)

class LspCodeLensListener(sublime_plugin.ViewEventListener):
    def __init__(self, view: sublime.View) -> None:
        super().__init__(view)
        self._stored_point = -1
        self.initialized = False
        self.enabled = False
        self.phantoms = []
        self.response_count = -1
        self.current_count = 0
        self.phantom_set = sublime.PhantomSet(self.view, 'code_lens')

    @classmethod
    def is_applicable(cls, _settings: 'Any') -> bool:
        syntax = _settings.get('syntax')
        is_supported = syntax and client_configs.is_syntax_supported(str(syntax))
        lsp_settings = sublime.load_settings("LSP.sublime-settings")
        disabled_by_user = 'codeLensProvider' in lsp_settings.get('disabled_capabilities', [])
        return is_supported and not disabled_by_user

    def on_activated_async(self) -> None:
        if not self.initialized:
            self.initialize()

    def initialize(self, is_retry: bool = False) -> None:
        sessions = list(sessions_for_view(self.view, 'codeLensProvider'))
        if sessions:
            self.initialized = True
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

    def on_text_changed(self) -> None:
        if self.enabled:
            self.schedule_request()

    def on_revert(self) -> None:
         if self.enabled:
            self.schedule_request()

    def schedule_request(self) -> None:
        sel = self.view.sel()
        if len(sel) < 1:
            return

        current_point = sel[0].b
        if self._stored_point != current_point:
            self._stored_point = current_point
            sublime.set_timeout_async(lambda: self.fire_request(current_point), 1000)

    def fire_request(self, current_point: int) -> None:
        if current_point == self._stored_point:
            self.send_code_lens_request()

    def send_code_lens_request(self) -> None:
        if is_transient_view(self.view):
            return

        session = find_session(self.view, 'codeLensProvider')
        if session:
            file_path = self.view.file_name()
            if file_path:
                params = {
                    "textDocument": {
                        "uri": filename_to_uri(file_path)
                    }
                }
                session.send_request(
                    Request('textDocument/codeLens', params),
                    self.handle_response
                )

    def handle_response(self, code_lens_response: 'Optional[List[dict]]') -> None:
        session = find_session(self.view, 'codeLensProvider')
        if session and code_lens_response:
            # print('handle_response', len(code_lens_response))
            self.phantoms = []
            self.current_count = 0
            self.response_count = len(code_lens_response)
            for code_lens in code_lens_response:
                session.send_request(
                    Request('codeLens/resolve', code_lens),
                    self.handle_resolve
                )

    def handle_resolve(self, response: 'Optional[List[dict]]') -> None:
        self.current_count += 1
        # print(self.current_count)
        range = Range.from_lsp(response['range'])
        region = range_to_region(range, self.view)

        content = "<small>{}</small>".format(response["command"]["title"])
        self.phantoms.append(sublime.Phantom(region, content, sublime.LAYOUT_BELOW))

        if self.current_count == self.response_count:
            self.current_count = 0
            self.response_count = -1
            print('apply', len(self.phantoms))
            self.phantom_set.update(self.phantoms)
