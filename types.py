from LSP.plugin.core.protocol import URI, Location, Range
from LSP.plugin.core.typing import TypedDict, List

ShowReference = TypedDict('ShowReference', {
    'references': List[Location],
    'uri': URI,
    'range': Range
})

ShowReferencesParams = List[ShowReference]
