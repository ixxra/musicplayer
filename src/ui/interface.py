from gi.repository import Gtk
from gi.repository import Gdk
import os.path


PLAYLIST = {
    'TITLE'         : 0,
    'ARTIST'        : 1,
    'ALBUM'         : 2,
    'LOCATION'      : 3,
    'ID'            : 4,
    'PLAYING_STATE' : 5
}


class Handler:
    def __init__(self, builder):
        self.builder = builder


    def on_playlist_button_press_event(self, widget, event):
        if event.triggers_context_menu() \
        and event.type == Gdk.EventType.BUTTON_PRESS:
            
            menu = self.builder.get_object('playlistMenu')
            button = event.button
            time = event.time
            menu.popup(None, None, None, None, button, time)

        return False


    def add_media_to_playlist(self, playlist):
        dialog = Gtk.FileChooserDialog(
            'Add media',
            None,
            Gtk.FileChooserAction.OPEN,
            (
                '_Cancel',
                Gtk.ResponseType.CANCEL,
                '_Open',
                Gtk.ResponseType.ACCEPT,
            )
        )
        dialog.set_select_multiple(True)

        res = dialog.run()
        if res == Gtk.ResponseType.ACCEPT:
            fnames = dialog.get_filenames()
            for fname in fnames:
                iter = playlist.append()
                playlist.set(iter, 
                    PLAYLIST['LOCATION'], fname,
                    PLAYLIST['TITLE'], os.path.basename(fname)
                )
        
        dialog.destroy()


    def remove_selection_from_playlist(self, selection):
        model, paths = selection.get_selected_rows()
        refs = [Gtk.TreeRowReference.new(model, p) for p in paths]
        for r in refs:
            iter = model.get_iter(r.get_path())
            model.remove(iter)

    def on_playlist_row_activated(self, treeview, path, column):
        print(treeview, path, column)

    def show_playlist_menu(self, action):
        print ('menu')
       
    def toggle_play(self, action):
        print ('toggle')

    def play(self, action):
        print('play')

    def next(self, action):
        print('next')

    def prev(self, action):
        print ('prev')

    def stop(self, action):
        print ('stop')
    
    def pause(self, action):
        print ('pause')

        
if __name__ == '__main__':
    b = Gtk.Builder.new_from_file('player.glade')
    h = Handler(b)
    b.connect_signals(h)

    mainWindow = b.get_object('mainWindow')

    mainWindow.connect('destroy', lambda w: Gtk.main_quit())
    mainWindow.show_all()

    Gtk.main()
