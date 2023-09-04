from mopidy.core.listener import CoreListener
from mopidy.core.actor import Core
from mopidy.models import TlTrack, Track
import threading
import pykka
import json
import os
import logging
import re

from . import Extension

logger = logging.getLogger(__name__)

class ProgressFrontend(pykka.ThreadingActor, CoreListener):
    def __init__(self, config: dict, core: Core):
        super(ProgressFrontend, self).__init__()
        self.core = core
        self.config = config
        self.state_path = os.path.join(Extension.get_data_dir(config), 'state.json')
        self.prog = self.load_progress()

        self.timer = PeriodicTimer.start(
            1, self.on_timer
        ).proxy()
        self.timer.start_ticking() # type: ignore

        self.persist_timer = PeriodicTimer.start(
            30, self.on_persist_timer
        ).proxy()
        self.persist_timer.start_ticking() # type: ignore

        logger.info('Initialized progress frontend!')

    ####### Config

    def should_remember(self, track: Track) -> bool:
        patterns = tuple( pattern for pattern in self.config['progress']['patterns'] )
        for pattern in patterns:
            if re.match(pattern, str(track.uri)):
                return True

        min_length_minutes = self.config['progress']['min_length_minutes']
        if min_length_minutes > 0 \
            and track.length is not None \
            and track.length > 1000 * 60 * min_length_minutes: # type: ignore
            return True
        return False

    ####### Events

    def track_playback_ended(self, tl_track: TlTrack, time_position: int):
        track: Track = tl_track.track # type: ignore

        if track.length is not None and time_position >= track.length: # type: ignore
            self.clear_progress_for(track)
        else:
            self.save_progress_for(track, time_position)

    def track_playback_started(self, tl_track: TlTrack):
        track: Track = tl_track.track # type: ignore

        prog = self.load_progress_for(track)
        if prog > 0:
            if self.core.playback is not None:
                self.core.playback.seek(prog)

    def on_timer(self):
        self.save_active_track_progress()

    def on_persist_timer(self):
        self.persist_progress()

    def on_stop(self) -> None:
        self.save_active_track_progress()
        self.persist_progress()
        self.timer.stop() #type: ignore
        self.persist_timer.stop() #type: ignore
        return super().on_stop()

    ####### FS access

    def load_progress(self) -> dict:
        prog: dict = {}

        # Load existing progress file if it exists
        if os.path.isfile(self.state_path):
            with open(self.state_path, 'r') as readfile:
                prog = json.loads(readfile.read())

        return prog

    def persist_progress(self):
        with open(self.state_path, 'w') as file:
            file.write(json.dumps(self.prog))

    ####### Actions

    def save_active_track_progress(self):
        track: Track | None = self.core.playback.get_current_track().get() # type: ignore
        progress = self.core.playback.get_time_position().get() # type: ignore
        if track is not None:
            self.save_progress_for(track, progress)

    def load_progress_for(self, track: Track) -> int:
        if self.should_remember(track):
            return self.prog.get(str(track.uri), -1)
        else:
            return -1

    def save_progress_for(self, track: Track, time_position: int):
        if self.should_remember(track):
            self.prog[str(track.uri)] = time_position

    def clear_progress_for(self, track: Track):
        self.prog.pop(str(track.uri), None)

class PeriodicTimer(pykka.ThreadingActor):
    def __init__(self, period, callback):
        super().__init__()
        self.period = period
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

