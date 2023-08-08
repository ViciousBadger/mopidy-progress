from mopidy.core.listener import CoreListener
from mopidy.core.actor import Core
from mopidy.core.playback import PlaybackController
from mopidy.models import TlTrack, Track
import threading
import pykka
import json
import os
import logging

from . import Extension

logger = logging.getLogger('mopidy_progress')

class ProgressFrontend(pykka.ThreadingActor, CoreListener):
    def __init__(self, config: dict, core: Core):
        super(ProgressFrontend, self).__init__()
        self.core = core
        self.config = config
        self.state_path = os.path.join(Extension.get_data_dir(config), 'state.json')

        self.timer = PeriodicTimer.start(
            1000, self.on_timer
        ).proxy()
        self.timer.start_ticking() # type: ignore

        logger.info('Initialized progress frontend!')

    ####### Events

    def track_playback_ended(self, tl_track: TlTrack, time_position: int):
        track: Track = tl_track.track # type: ignore

        identifier = str(track.uri)

        if time_position >= track.length: # type: ignore
            logger.info('playback ended at end of track, clearing saved progress for %s', track.uri)
            self.clear_progress_for(identifier)
        else:
            logger.info('playback ended prematurely, saving track progress for %s', track.uri)
            self.save_progress_for(identifier, time_position)

    def track_playback_started(self, tl_track: TlTrack):
        track: Track = tl_track.track # type: ignore

        prog = self.load_progress_for(str(track.uri))
        if prog > 0:
            logger.info('restoring last saved playback time for %s', track.uri)
            if self.core.playback is not None:
                self.core.playback.seek(prog)

    def on_timer(self):
        track: Track | None = self.core.playback.get_current_track().get() # type: ignore
        if track:
            logger.info('track!!! %s', str(track.name))

    def on_stop(self) -> None:
        logger.info('on stop')

        self.save_active_track_progress()

        self.timer.stop() #type: ignore
        return super().on_stop()

    ####### FS access

    def load_progress(self) -> dict:
        prog: dict = {}

        # Load existing progress file if it exists
        if os.path.isfile(self.state_path):
            with open(self.state_path, 'r') as readfile:
                prog = json.loads(readfile.read())

        return prog

    def save_progress(self, prog: dict):
        with open(self.state_path, 'w') as file:
            file.write(json.dumps(prog))
        logger.info('Progress saved to %s', self.state_path)

    ####### Actions

    def save_active_track_progress(self):
        track: Track | None = self.core.playback.get_current_track().get() # type: ignore
        progress = self.core.playback.get_time_position().get() # type: ignore
        if track is not None:
            self.save_progress_for(str(track.uri), progress)
            logger.info('saved active track progress %d', progress)

    def load_progress_for(self, identifier: str) -> int:
        prog = self.load_progress()
        return prog.get(identifier, -1)

    def save_progress_for(self, identifier: str, time_position: int):
        prog = self.load_progress()
        prog[identifier] = time_position
        self.save_progress(prog)

    def clear_progress_for(self, identifier: str):
        prog = self.load_progress()
        prog.pop(identifier)
        self.save_progress(prog)

class PeriodicTimer(pykka.ThreadingActor):
    def __init__(self, period, callback):
        super().__init__()
        self.period = period / 1000.0
        self.stop_pending = False
        self.callback = callback

    def start_ticking(self):
        self._periodic()

    def stop_ticking(self):
        self.stop_pending = True

    def on_stop(self):
        self.stop_ticking()

    def _periodic(self):
        if self.stop_pending:
            return
        self.callback()
        threading.Timer(self.period, self._periodic).start()

