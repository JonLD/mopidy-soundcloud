import logging

import pykka

from mopidy import backend
from mopidy_soundcloud.library import SoundCloudLibraryProvider
from mopidy_soundcloud.soundcloud import SoundCloudClient

logger = logging.getLogger(__name__)


class SoundCloudBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super().__init__()
        self.config = config
        self.remote = SoundCloudClient(config)
        self.library = SoundCloudLibraryProvider(backend=self)
        self.playback = SoundCloudPlaybackProvider(audio=audio, backend=self)

        self.uri_schemes = ["soundcloud", "sc"]



class SoundCloudPlaybackProvider(backend.PlaybackProvider):
    def translate_uri(self, uri):
        track_id = self.backend.remote.parse_track_uri(uri)
        track = self.backend.remote.get_track(track_id, True)
        if track is None:
            return None
        return track.uri
