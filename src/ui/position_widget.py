from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gst


class PositionWidget(Gtk.Scale):
    def __init__(self, playbin, orientation=Gtk.Orientation.HORIZONTAL):
        Gtk.Scale.__init__(self, orientation=orientation)
        adj = self.get_adjustment()
        adj.set_lower(0.0)
        #adj.set_upper(1.0)
        adj.set_step_increment(1)

        bus = playbin.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self.on_eos)
        bus.connect('message::duration_changed', self.on_duration_changed)
        bus.connect('message::async_done', self.on_async_done)
        bus.connect('message::state_changed', self.on_state_changed)
        bus.connect('message::error', self.on_error)
        bus.connect('message::tag', self.on_tag)


        GLib.timeout_add(1000, self.update_position)

        self.pos = 0
        self.playbin = playbin
        self.update_duration()

        self.connect('format-value', self.display_position)



    def update_duration(self):
        print ('duration:', self.playbin.query_duration(Gst.Format.TIME))
        


    def on_eos(self, bus, message):
        self.set_value(0.0)
    
    def on_duration_changed(self, bus, message):
        print ('duration changed')
        self.update_duration() 

    def on_async_done(self, bus, message):
        print ('async done')


    def on_state_changed(self, bus, message):
        old_state, new_state, pending_state = message.parse_state_changed()
        print (old_state, new_state, pending_state)

    def on_error(self, bus, message):
        print ('error', message)

    def on_tag(self, bus, message):
        print (message.parse_tag())

    def update_position(self):
        ok_pos, pos = self.playbin.query_position(Gst.Format.TIME)
        ok_dur, dur = self.playbin.query_duration(Gst.Format.TIME)

        if ok_dur:
            self.get_adjustment().set_upper(dur/10**9)

        if ok_pos:
            self.set_value(pos/10**9)
        else:
            self.set_value(0.0)

        return True


    def display_position(self, scale, value):
        secs = int(value)
        min = secs // 60
        secs %= 60
        return '{0}:{1}'.format(min, secs)


if __name__ == '__main__':
    from sys import argv

    Gtk.init(argv)
    Gst.init(argv)

    w = Gtk.Window()
    
    pb = Gst.ElementFactory.make('playbin', 'playbin')
    
    w.add(PositionWidget(pb))
    w.connect('destroy', lambda w: Gtk.main_quit())

    pb.set_state(Gst.State.NULL)
    pb.set_property('uri', Gst.filename_to_uri(argv[1]))
    pb.set_state(Gst.State.PLAYING)

    w.show_all()
    w.resize(400, 400)

    Gtk.main()

