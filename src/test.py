from extractor import Extractor
from gi.repository import Gst
from gi.repository import GLib
from models import Track
import os


MUSIC_DIR = '/home/isra/Music'


def save_and_quit(extractor):
    for meta in extractor.metadata:
        fname = meta.pop('fname')
        t = Track(fname, meta)
        t.save()
    loop.quit()


Gst.init()
ex = Extractor()


for f in os.listdir('/home/isra/Music'):
    if f[-4:] == '.mp3':
        print (f)
        ex.add_to_queue(os.path.join(MUSIC_DIR, f))

loop = GLib.MainLoop()
ex.finished.connect(save_and_quit)
ex.start()
loop.run()
