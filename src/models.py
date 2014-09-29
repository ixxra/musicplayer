import collections as coll
import sqlite3 as db


MUSIC_DIR = '~/Music'
DATABASE = 'database.db'


_Metadata = coll.namedtuple('Metadata', ['key', 'value'])

class Track:
    def __init__(self, uri:str, metadata:dict):
        assert isinstance(uri, str)
        assert isinstance(metadata, dict)
        
        self.uri = uri
        self.metadata = metadata
        self.id = None


    def save(self):
        db = Track.get_connection()
        c = db.cursor()
        try:
            c.execute('''
                insert or abort into files (uri) values (:uri)
            ''', 
                {'uri': self.uri}
            )
        except db.IntegrityError:
            pass
        db.commit()

        self.id, = c.execute('''
                select rowid from files where uri=:uri
        ''', {'uri': self.uri}).fetchone()


        for k, values in self.metadata.items():
            for v in values:
                try:
                    c.execute('''
        insert into tags (key, value, file_id) values (:key, :value,:file_id) 
        ''', {'key':k, 'value': v, 'file_id': self.id})
                except Exception as e:
                    print ('Exception:', e)
                    print('Error:', k, v, self.id)
        db.commit()


    def __repr__(self):
        nice = {'title': None, 'artist': None}

        if 'title' in self.metadata:
            nice['title'] = ','.join(self.metadata['title'])
        else:
            nice['title'] = self.uri

        if 'artist' in self.metadata:
            nice['artist'] = ','.join(self.metadata['artist'])

        if nice['artist'] is not None:
            return '<track info: {title} - {artist}>'.format(**nice)
        else:
            return '<track info: {}>'.format(nice['title'])
   

    @staticmethod
    def find(value):
        db = Track.get_connection()
        c = db.cursor()
        c.execute('''
        select key, value, file_id from tags where file_id in (
        select file_id from tags where value like ?)
        ''', ('%{}%'.format(value),))
        
        data = {}
        
        for key, value, file_id in c:
            if file_id not in data:
                data[file_id] = {key: value}
            elif key not in data[file_id]:
                data[file_id][key] = [value]
            else:
                data[file_id][key].append(value)
                

        ans = []

        for file_id, meta in data.items():
            uri, = c.execute('''
            select uri from files where rowid=?
            ''', (file_id,)).fetchone()
            t = Track(uri, meta)
            t.id = file_id
            ans.append(t)

        return ans
           

    @staticmethod
    def count():
        db = Track.get_connection()
        c = db.cursor()
        total, = c.execute('''
                select count(*) from files
                ''').fetchone();

        return total

    
    @staticmethod
    def all():
        db = Track.get_connection()
        c = db.cursor()
        c.execute('select uri, rowid from files')

        tracks = []
        for uri, file_id in c:
            meta = {}
            meta_c = db.cursor()
            meta_c.execute('''
                    select key, value from tags where file_id=:file_id
            ''', {'file_id':file_id})

            for key, value in meta_c:
                if key not in meta:
                    meta[key] = [value]
                else:
                    meta[key].append(value)
                    
            tracks.append(Track(uri, meta))
        return tracks

    

    @staticmethod
    def get_connection():
        return db.connect(DATABASE)

