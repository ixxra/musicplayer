from gi.repository import Gst
from gi.repository import GLib
from gi.repository import GObject
import os


class Player(GObject.Object):
    def __init__(self):
        GObject.Object.__init__(self)
        self.queue = []
        self.metadata = {}


    @GObject.Signal
    def finished(self):
        self.stop()
        delattr(self, 'pipe')


    def play_next(self):
        try:
            fname = self.queue.pop(0)
        except:
            self.finished.emit()
            return
            
        uri = Gst.filename_to_uri(fname)

        if not hasattr(self, 'pipe'):
            self.make_pipe()

        self.pipe.set_state(Gst.State.NULL)
        self.pipe.set_property('uri', uri)
        self.pipe.set_state(Gst.State.PLAYING)


    def stop(self):
        self.pipe.set_state(Gst.State.NULL)


    def append(self, fname):
        self.queue.append(os.path.abspath(fname))


    def append_many(self, files):
        self.queue.extend(map(os.path.abspath, files))


    def make_pipe(self):
        self.pipe = Gst.ElementFactory.make('playbin', 'playbin')
        self.connect_bus()


    def connect_bus(self):
        bus = self.pipe.get_bus()
        bus.add_signal_watch()
        bus.connect('message::tag', self.on_tag)
        bus.connect('message::eos', self.on_eos)
        bus.connect('message::error', self.on_error)


    def on_tag(self, bus, message):
        def get_value(taglist, key):
            for i in range(taglist.get_tag_size(key)):
                value = taglist.get_value_index(key, i)
                if isinstance(value, Gst.DateTime):
                    value = value.to_iso8601_string()
                if value is None:
                    continue
                try:
                    metadata[key].add(value)
                except KeyError:
                    metadata[key] = set([value])

        metadata = {}
        message.parse_tag().foreach(get_value)
        self.metadata = metadata


    def on_eos(self, bus, message):
        self.metadata.clear()
        self.play_next()


    def on_error(self, message, bus):
        print ('Error:')
        print (message.parse_error())
        