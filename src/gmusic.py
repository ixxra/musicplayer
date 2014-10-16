from gi.repository import Gtk
from gi.repository import Gst
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

        if self.playingRef is not None:
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



Gst.init(argv)
Gtk.init(argv)

b = Gtk.Builder.new_from_file('ui/player.glade')
GMusic(b)

Gtk.main()
