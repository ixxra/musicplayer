from gi.repository import Gtk
from gi.repository import Gst
from sys import argv
import extractor as ex
import os.path


METADATA = {
    'KEY': 0,
    'VALUE': 1
}


class SignalsHandler:
    fnameLabel = None
    coverArt = None
    metadataModel = None
    spinner = None


    def __init__(self, uiBuilder):
        self.fnameLabel = uiBuilder.get_object('fnameLabel')
        self.coverArt = uiBuilder.get_object('coverArt')
        self.metadataModel = uiBuilder.get_object('metadataModel')
        self.spinner = uiBuilder.get_object('spinner')
        self.extractor = ex.Extractor()
        self.extractor.finished.connect(self.show_metadata, self.metadataModel)

    def openMedia_activate_cb(self, action):
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

        res = dialog.run()
        if res == Gtk.ResponseType.ACCEPT:
            fname = dialog.get_filename()
            self.fnameLabel.set_text(os.path.basename(fname))
            self.fnameLabel.set_tooltip_text(fname)
            self.metadataModel.clear()
            self.extractor.clear_all()
            self.extractor.add_to_queue(fname)
            self.extractor.start()
            self.spinner.show()
            self.spinner.start()


        dialog.destroy()


    def show_metadata(self, extractor, model):
        metadata = extractor.metadata[0]
        for k, s in metadata.items():
            for v in s:
                iter = model.append()
                model.set(iter, 
                        METADATA['KEY'], k,
                        METADATA['VALUE'], str(v))
            
                if isinstance(v, Gst.Sample):
                    print(k, v, type(v))
                    print(v.get_buffer())
        self.spinner.stop()
        self.spinner.hide()


Gtk.init(argv)
Gst.init(argv)

b = Gtk.Builder()
b.add_from_file('ui/metadata_inspector.glade')
b.connect_signals(SignalsHandler(b))

window = b.get_object('mainWindow')
window.connect('destroy', lambda w: Gtk.main_quit())
window.resize(500, 600)
window.show()

Gtk.main()
