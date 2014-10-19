from gi.repository import Gst
from gi.repository import GLib
from gi.repository import GObject
import os


class Extractor(GObject.Object):
    def __init__(self):
        GObject.Object.__init__(self)
        self.make_pipe()
        self.connect_bus()
        self.files = []
        self.metadata = []
        self.queue = []

    @GObject.Signal
    def finished(self):
        return

    def add_to_queue(self, fname):
        '''
        Adds fname to queue for metadata extraction.
        This is a FIFO queue
        '''
        self.queue.append(os.path.abspath(fname))

    def clear_all(self):
        '''
        Clears queue, filenames list and metadata cache.
        Raises an exception if the inner pipe is in the PLAYING state.
        '''
        assert self.pipe.get_state(Gst.CLOCK_TIME_NONE) \
                != Gst.State.PLAYING, 'Extractor is working!'
        self.pipe.set_state(Gst.State.NULL)
        self.files.clear()
        self.metadata.clear()
        self.queue.clear()

    def start(self):
        assert len(self.queue) > 0
        fname = self.queue.pop(0)
        self.files.append(fname)
        self.metadata.append({'fname': {fname}})
        uri = Gst.filename_to_uri(fname)

        self.pipe.set_state(Gst.State.NULL)
        self.pipe.get_by_name('decoder').set_property('uri', uri)
        self.pipe.set_state(Gst.State.PLAYING)

    @staticmethod
    def link_pads_and_go(decoder, src_pad, pipe):
        sink = pipe.get_by_name('sink')
        sink_pad = sink.pads[0]

        print('Linking pads: {p} -> {s}'.format(
            p=src_pad.name, s=sink_pad.name)
        )
        src_pad.link(sink_pad)

    def add_tag(self, bus, message):
        def get_value(taglist, key):
            for i in range(taglist.get_tag_size(key)):
                value = taglist.get_value_index(key, i)
                if isinstance(value, Gst.DateTime):
                    value = value.to_iso8601_string()
                if value is None:
                    continue
                try:
                    self.metadata[-1][key].add(value)
                except KeyError:
                    self.metadata[-1][key] = set([value])

        message.parse_tag().foreach(get_value)

    def raise_error(self, bus, message):
        print('ERROR!:')
        print(message.parse_error())
        self.process_next()

    def on_eos(self, bus, message):
        self.process_next()

    #def process_next(self, bus, message, pipe):
    def process_next(self):
        print('got EOS')

        try:
            fname = self.queue.pop(0)
            self.files.append(fname)
            self.metadata.append({'fname': fname})
        except IndexError:
            self.pipe.set_state(Gst.State.NULL)
            print('No more files on queue')
            print(self.files)
            print(self.metadata)
            self.finished.emit()
            return

        print('fname:', fname)
        uri = Gst.filename_to_uri(fname)

        self.pipe.set_state(Gst.State.NULL)
        self.pipe.get_by_name('decoder').set_property('uri', uri)
        self.pipe.set_state(Gst.State.PLAYING)

    def make_pipe(self):
        decoder = Gst.ElementFactory.make('uridecodebin', 'decoder')
        sink = Gst.ElementFactory.make('fakesink', 'sink')
        pipe = Gst.Pipeline()
        pipe.add(decoder)
        pipe.add(sink)
        pipe.get_bus().add_signal_watch()

        decoder.connect('pad-added', self.link_pads_and_go, pipe)
        decoder.connect('pad-removed', lambda d, p: print('pad removed!'))

        self.pipe = pipe

    def connect_bus(self):
        bus = self.pipe.get_bus()
        bus.connect('message::tag', self.add_tag)
        bus.connect('message::eos', self.on_eos)
        bus.connect('message::error', self.raise_error)


if __name__ == '__main__':
    from sys import argv

    def print_and_bye(extractor):
        print(extractor.metadata)
        loop.quit()

    Gst.init()

    ex = Extractor()

    for fname in argv[1:]:
        ex.add_to_queue(fname)

    loop = GLib.MainLoop()
    ex.finished.connect(print_and_bye)
    ex.start()
    loop.run()
