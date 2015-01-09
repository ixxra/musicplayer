from gi.repository import Gtk
from gi.repository import Gst
from gi.repository import GLib
from sys import argv
import player as pl
import ui.interface as iface


class GMusic(iface.Handler):
    playingRef = None
    mainWindow = None

    def __init__(self, builder):
        iface.Handler.__init__(self, builder)
        builder.connect_signals(self)
        self.player = pl.Player()
        self.player.finished.connect(self.on_player_finished)

        mainWindow = builder.get_object('mainWindow')
        mainWindow.connect('destroy', lambda w: Gtk.main_quit())
        mainWindow.show_all()

        self.mainWindow = mainWindow
        self.posAdj = builder.get_object('positionAdjustment')

        self.update_interface_ID = GLib.timeout_add(500, self.update_interface)

    def on_playlist_row_activated(self, treeview, path, column):
        model = treeview.get_model()
        self.play_selected(model, path)

    def on_player_finished(self, player):
        model = self.playingRef.get_model()
        path = self.playingRef.get_path()
        iter = model.get_iter(path)
        next = model.iter_next(iter)

        if next is not None:
            self.play_selected(model, model.get_path(next))

    def play_selected(self, model, path):
        iter = model.get_iter(path)
        fname, title, = model.get(
            iter,
            iface.PLAYLIST['LOCATION'],
            iface.PLAYLIST['TITLE']
        )
        self.player.queue.clear()
        self.player.append(fname)
        self.player.play_next()
        self.mainWindow.set_title(title)

        if self.playingRef is not None and self.playingRef.valid():
            old_path = self.playingRef.get_path()
            old_iter = model.get_iter(old_path)
            model.set(old_iter, iface.PLAYLIST['PLAYING_STATE'], None)

        model.set(iter, iface.PLAYLIST['PLAYING_STATE'], Gtk.STOCK_MEDIA_PLAY)
        self.playingRef = Gtk.TreeRowReference.new(model, path)

    def toggle_play(self, action):
        self.player.toggle_state()

    def play(self, action):
        self.player.play_next()

    def stop(self, action):
        self.player.stop()

    def pause(self, action):
        self.player.pause()

    def on_positionBar_button_press_event(self, posBar, ev):
        GLib.source_remove(self.update_interface_ID)

    def on_positionBar_button_release_event(self, posBar, ev):
        if not hasattr(self.player, 'pipe'):
            return True

        pipe = self.player.pipe
        dur_ok, dur = pipe.query_duration(Gst.Format.TIME)

        if dur_ok:
            new_pos = posBar.get_value() * dur
            pipe.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, new_pos)

        self.update_interface_ID = GLib.timeout_add(500, self.update_interface)

    def update_interface(self):
        if not hasattr(self.player, 'pipe'):
            return True
        pipe = self.player.pipe
        pos_ok, pos = pipe.query_position(Gst.Format.TIME)
        dur_ok, dur = pipe.query_duration(Gst.Format.TIME)
        if pos_ok and dur_ok:
            self.posAdj.set_value(pos/dur)
        #GLib.print("Time: %" + Gst.TIME_FORMAT + "/ %" + Gst.TIME_FORMAT + "\r", Gst.Time.Args(pos), Gst.Time.Args(dur))
        return True


Gst.init(argv)
Gtk.init(argv)

b = Gtk.Builder.new_from_file('ui/player.glade')
GMusic(b)

Gtk.main()
