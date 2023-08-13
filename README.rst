****************************
Mopidy-Progress
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-Progress
    :target: https://pypi.org/project/Mopidy-Progress/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/github/actions/workflow/status/ViciousBadger/mopidy-progress/CI?branch=main
    :target: https://github.com/ViciousBadger/mopidy-progress/actions
    :alt: CI build status

.. image:: https://img.shields.io/codecov/c/gh/ViciousBadger/mopidy-progress
    :target: https://codecov.io/gh/ViciousBadger/mopidy-progress
    :alt: Test coverage

Remember and restore playback progress for specified tracks.

The extension can be configured to save progress on any track you want to based on pattern matching, meaning you can enable it only for relevant media, e.g. podcasts and audiobooks.

Progress is saved continually while a track is being played. Whenever that same track is played again, the extension will restore the saved progress so you can listen from where you left off.

When a track is played to its end, the saved progress will reset. It is also possible to reset the saved progress by stopping (not pausing) the track.


Installation
============

Install by running::

    python3 -m pip install Mopidy-Progress


Configuration
=============

The default configuration looks like this::

    [progress]
    enabled = true
    min_length_minutes = 30
    patterns =

        ^podcast\+

With the defaults, progress will be saved for tracks from the Mopidy-Podcast extension and tracks that are longer than 30 minutes. Other tracks will always play from the beginning as normal.

To change this behaviour, you must add configuration for
Mopidy-Progress to your Mopidy configuration file::

    [progress]
    enabled = true
    min_length_minutes = [integer]
    patterns = 

        [pattern],
        [pattern],
        ...

The 'patterns' setting determines which tracks progress will be remembered for based on their track URI.

You can find the URI of a track in several ways, one of them being adding the track to any playlist and then opening the playlist file in a text editor. (By default playlists are stored in ~/.local/share/mopidy/m3u/)

Patterns use regular expression matching. Be aware that some symbols will have special meaning in regular expressions and must be escaped, like the '+' symbol this pattern:

    ^podcast\+

The above pattern matches any track with an URI starting with 'podcast+', which will be any track from the Mopidy-Podcast extension.

Another example of an expression could be:

    ^local:track:Audiobooks

This one matches all tracks in a special user-defined directory of the Mopidy-Local extension. For more information on such directories, consult the readme for [Mopidy-Local](https://github.com/mopidy/mopidy-local).

Project resources
=================

- `Source code <https://github.com/ViciousBadger/mopidy-progress>`_
- `Issue tracker <https://github.com/ViciousBadger/mopidy-progress/issues>`_
- `Changelog <https://github.com/ViciousBadger/mopidy-progress/blob/master/CHANGELOG.rst>`_


Credits
=======

- Original author: `badgerson <https://github.com/ViciousBadger>`__
- Current maintainer: `badgerson <https://github.com/ViciousBadger>`__
- `Contributors <https://github.com/ViciousBadger/mopidy-progress/graphs/contributors>`_
