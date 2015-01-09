from extractor import Extractor
from gi.repository import Gst
from gi.repository import GLib
from models import Track
import json
import os
from sys import argv


MUSIC_DIR = '/home/isra/Music'


def save(extractor, metadataId):
    metadata = extractor.metadata[metadataId]
    fname = metadata.pop('fname')
    t = Track(fname, metadata)
    t.save()


#def save_and_quit(extractor):
#    for meta in extractor.metadata:
#        fname = meta.pop('fname')
#        t = Track(fname, meta)
#        t.save()
#    loop.quit()


Gst.init()
ex = Extractor()


for f in argv[1:]:
    path = os.path.abspath(f)
    if not Track.exists(path):
        ex.add_to_queue(path)
    else:
        print(f, 'exists in dabase. Skiping')

loop = GLib.MainLoop()
ex.eos.connect(save)
ex.finished.connect(lambda ex: loop.quit())
#ex.finished.connect(save_and_quit)
ex.start()
loop.run()
