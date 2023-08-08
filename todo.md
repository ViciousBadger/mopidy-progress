- To restore state:
PlaybackController.seek(ms)

React to
- track_playback_ended(tl_track, time_position)
    - check if time should be saved
    - (read Track.uri and look for prefix, eg "podcast+{uri}" or "local:track:Audiobooks")
        - save time
        - how to deal with track being fully played? delete time file?
- track_playback_started(tl_track)
    - check if time should be loaded
        - check if a state file exists
            - load time with PlaybackController.seek

