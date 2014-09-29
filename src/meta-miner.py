from gi.repository import Gst
from gi.repository import GLib
from sys import argv
import pickle


def link_pads_and_go(decoder, src_pad, pipe):
    sink = pipe.get_by_name('sink')
    sink_pad = sink.pads[0]

    print ('Linking pads: {p} -> {s}'.format(
            p=src_pad.name, s=sink_pad.name
        )
    )
    src_pad.link(sink_pad)


def add_tag(bus, message):
    def get_value(taglist, key):
        if key in latest_tag:
            return

        latest_tag[key] = []

        for i in range(taglist.get_tag_size(key)):
            value = taglist.get_value_index(key, i)
            latest_tag[key].append(value)

    message.parse_tag().foreach(get_value)
    #print (tags.to_string())


def raise_error(bus, message):
    print ('ERROR!:')
    print (message.parse_error())


def process_next(bus, message):
    print ('got EOS')
    
    if 'datetime' in latest_tag:
        del latest_tag['datetime']
    
    tags.append(latest_tag)
    
    global latest_tags
    latest_tags = {}

    try:
        fname = fnames.pop(0)
    except IndexError:
        print ('No more files to process, exit')

        with open('metadata.pickle', 'wb') as f:
            pickle.dump(tags, f)

        loop.quit()
        return False

    print ('fname:', fname)
    uri = Gst.filename_to_uri(fname)
    latest_tag['uri'] = uri

    pipe.set_state(Gst.State.NULL)
    pipe.get_by_name('decoder').set_property('uri', uri)
    pipe.set_state(Gst.State.PLAYING)


def message_handler(bus, message):
    print (Gst.MessageType.get_name(message.type))
    

def make_pipe():
    decoder = Gst.ElementFactory.make('uridecodebin', 'decoder')
    sink = Gst.ElementFactory.make('fakesink', 'sink')
    pipe = Gst.Pipeline()
    pipe.add(decoder)
    pipe.add(sink)
    pipe.get_bus().add_signal_watch()
    
    decoder.connect('pad-added', link_pads_and_go, pipe)
    decoder.connect('pad-removed', lambda d, p: print('pad removed!'))

    return pipe


Gst.init()

fnames = argv[1:]
pipe = make_pipe()
pipe.set_state(Gst.State.NULL)

tags = []
latest_tag = {}

bus = pipe.get_bus()
bus.connect('message::tag', add_tag)
bus.connect('message::eos', process_next)
bus.connect('message::error', raise_error)

fname = fnames.pop(0)
uri = Gst.filename_to_uri(fname)
latest_tag['uri'] = uri

pipe.get_by_name('decoder').set_property('uri', uri)
pipe.set_state(Gst.State.PLAYING)


loop = GLib.MainLoop()
loop.run()

