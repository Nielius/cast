"""Command line utility to control your Google Chromecast.

Usage:
    cast next
    cast pause
    cast play
    cast status
    cast toggle
    cast seek <second>
    cast rewind
    cast volume [<value>]

Options:
    -h --help       Show this text.
    -v --version    Show current version.
"""

from docopt import docopt
import pychromecast
import time
import logging

from ConfigParser import ConfigParser
from os.path import expanduser

# Parse config file into constants.
config = ConfigParser()
config.read(expanduser('~/.config/cast/config.ini'))

CHROMECAST_HOST = config.get('cast', 'chromecast_ip')
SLEEP_TIME = float(config.get('cast', 'sleep_time'))


def _to_minutes(seconds):
    """ Make a nice time string from the given seconds. """
    return '%d:%d' % divmod(seconds, 60)


def _volume_command(cast, volume):
    """ Set the value if a volume level is provided, else print the current
    volume level. """
    if volume is not None:
        cast.set_volume(float(volume))
    else:
        print cast.status.volume_level


def _status_command(cast, mc):
    """ Build a nice status message and print it to stdout. """
    if mc.is_playing:
        play_symbol = u'\u25B6'
    else:
        play_symbol = u'\u2759\u2759'

    print u' %s %s by %s from %s via %s, %s of %s' % (
        play_symbol,
        mc.title,
        (mc.artist if hasattr(mc, "artist") else "Unknown artist"),
        (mc.album if hasattr(mc, "album") else "Unknown album"),
        cast.app_id,
        _to_minutes(mc.status.current_time),
        _to_minutes(mc.status.duration)
    )


def main():
    """ Read the options given on the command line and do the required actions.

    This method is used in the entry_point `cast`.
    """
    opts = docopt(__doc__, version="cast 0.1")

    cast = pychromecast.Chromecast(CHROMECAST_HOST)
    mc = cast.media_controller

    # Wait for ramp connection to be initted.
    time.sleep(SLEEP_TIME)

    if mc is None:
        print 'Chromecast is not up or something else is wrong'
        return 1

    print opts

    if opts['next']:
        # next in old version is skip in the new version?
        mc.skip()
    elif opts['pause']:
        mc.pause()
    elif opts['play']:
        mc.play()
    elif opts['toggle']:
        print "Doesn't work?"
        mc.playpause()
    elif opts['seek']:
        mc.seek(opts['<second>'])
    elif opts['rewind']:
        mc.rewind()
    elif opts['status']:
        _status_command(cast, mc)
    elif opts['volume']:
        _volume_command(cast, opts['<value>'])

    # Wait for command to be sent.
    time.sleep(SLEEP_TIME)

main()
