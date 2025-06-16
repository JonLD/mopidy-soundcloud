import collections
import logging
import re
import urllib.parse

from mopidy import backend, models
from mopidy.models import SearchResult, Track

logger = logging.getLogger(__name__)


def generate_uri(path):
    return f"soundcloud:directory:{urllib.parse.quote('/'.join(path))}"



def simplify_search_query(query):
    if isinstance(query, dict):
        r = []
        for v in query.values():
            if isinstance(v, list):
                r.extend(v)
            else:
                r.append(v)
        return " ".join(r)
    if isinstance(query, list):
        return " ".join(query)
    else:
        return query

class SoundCloudLibraryProvider(backend.LibraryProvider):
    root_directory = models.Ref.directory(
        uri="soundcloud:directory", name="SoundCloud"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def search(self, query=None, uris=None, exact=False):
        # TODO Support exact search
        logger.info(f"[SoundCloud] Search called with query: {query}")
        if not query:
            logger.info(f"[SoundCloud] no query: {query}")
            return

        if "uri" in query:
            logger.info(f"[SoundCloud] uri query: {query}")
            search_query = "".join(query["uri"])
            url = urllib.parse.urlparse(search_query)
            if "soundcloud.com" in url.netloc:
                logger.info(f"Resolving SoundCloud for: {search_query}")
                return SearchResult(
                    uri="soundcloud:search",
                    tracks=self.backend.remote.resolve_url(search_query),
                )
        else:
            search_query = simplify_search_query(query)
            logger.info(f"Searching SoundCloud for: {search_query}")
            return SearchResult(
                uri="soundcloud:search",
                tracks=self.backend.remote.search(search_query),
            )

    def lookup(self, uri):
        if "sc:" in uri:
            uri = uri.replace("sc:", "")
            return self.backend.remote.resolve_url(uri)

        try:
            track_id = self.backend.remote.parse_track_uri(uri)
            track = self.backend.remote.get_track(track_id)
            if track is None:
                logger.info(
                    f"Failed to lookup {uri}: SoundCloud track not found"
                )
                return []
            return [track]
        except Exception as error:
            logger.error(f"Failed to lookup {uri}: {error}")
            return []
