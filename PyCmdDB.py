#!/usr/bin/env python
# encoding: utf-8
"""
This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from string import letters, digits

from os import path as fs

try:
    import cPickle as pickle
except ImportError:
    import pickle

backends = {}

def _validate_key(key):
    allowed_chars = letters + digits + '_- '
    check = str(key).translate(None, allowed_chars)
    if len(check) > 0:
        raise KeyError('Invalid characters found in the key specified: %s' % ', '.join(list(check)))
    return True


def get_db_backend(data_dir, dbname, backend='pickle'): pass


def unimplemented(func):
    def not_implemented_func(*args, **kwargs):
        raise NotImplementedError('This method is not currently implemented on this backend!')

    not_implemented_func.unimplemented = True
    return not_implemented_func


class dbbackend(object):
    def __init__(self):
        self.__imports__ = {}
        self.__deps__ = {}

    def setupdeps(self, f):
        fc = f.func_code
        fa = [] if fc.co_argcount is None or fc.co_argcount == 0 else list(fc.co_varnames[0:fc.co_argcount])
        fd = [] if f.func_defaults is None else list(f.func_defaults)
        fa.reverse()
        fd.reverse()
        ldefaults = len(fd)
        for i, k in enumerate(fa):
            self.__deps__[k] = k\
            if i >= ldefaults else fd[i]
        fa.reverse()
        return fa

    def __call__(self, f):
        global backends
        argkeys = self.setupdeps(f)
        args = []
        for depk in argkeys:
            dep = self.__deps__[depk]
            try: self.__imports__[depk] = __import__(dep)
            except ImportError:
                try: self.__imports__[depk] = __import__(depk)
                except ImportError: return get_db_backend
            args.append(self.__imports__[depk])

        def backendf(data_dir, dbname):
            backendcls = f(*args)
            return backendcls(data_dir, dbname)

        fn = f.func_name[9:]
        backendf.__doc__ = """ Constructs the target backend. """
        backends[fn] = backendf
        return backendf


class BaseBackend(object):
    __auto_open__ = True
    # We can iterate by index regardless. This is just to tell whether or not we should
    # allow the keys to be numerical on the creation of a new item.
    __numeric_keys__ = False

    def __init__(self, data_dir, dbname):
        self.data_dir = data_dir
        self.database = dbname
        self.dbfile = None
        self.db = None
        if hasattr(self._deleteall, 'unimplemented') and self._deleteall.unimplemented:
            self._deleteall = None
        if hasattr(self._getrange, 'unimplemented') and self._getrange.unimplemented:
            self._getrange = None
        if self.__auto_open__:
            self._open()

    def flush(self):
        self._flush()

    def _fpath(self): return fs.join(self.data_dir, self.database)

    def _resolve_key(self, tkey, action):
        action = '_' + action
        if tkey in [int, long]:
            action += 'i'
        elif tkey in [str, unicode]:
            action += 'a'
        else:
            raise KeyError('Unrecognized key type. Expected one of the following: str, unicode, int, long')
        return getattr(self, action)

    def __enter__(self):
        self._open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._flush()
        self._close()

    def has(self, key):
        check = self.get(key)
        return check is not None

    def get(self, key=None):
        if key is None:
            if self._getrange is None:
                result = []
                for k in self.keys():
                    result.append((k, self.get(k)))
                return result
            else:
                return self._getrange()
        action = self._resolve_key(type(key), 'get')
        return action(key)

    def delete(self, key=None):
        if key is None:
            if self._deleteall is None:
                for k in self.keys():
                    self.delete(k)
                return
            else:
                return self._deleteall()
        action = self._resolve_key(type(key), 'delete')
        return action(key)

    def put(self, *args):
        args = list(args)
        if len(args) == 0:
            raise Exception('You must specify a value.')
        elif len(args) == 1:
            if not self.__numeric_keys__:
                raise Exception('You must specify a string or unicode key for this new entry!')
            key = self.index()
            val = args[0]
        elif len(args) == 2:
            key = args[0]
            val = args[1]
        else:
            key = args[0]
            val = args[1:]
        action = self._resolve_key(type(key), 'put')
        return action(key, val)

    def _geti(self, index):
        try:
            key = self._i2a(index)
        except KeyError:
            return None
        return self._geta(key)

    def _deletei(self, index):
        self._deletea(self._i2a(index))

    def _puti(self, index, val):
        try: key = self._i2a(index)
        except KeyError, ex:
            if self.__numeric_keys__:
                self._puta(index, val)
            else: raise ex

    @unimplemented
    def _i2a(self, index): pass

    @unimplemented
    def keys(self): pass

    @unimplemented
    def _getrange(self, start=None, stop=None): pass

    @unimplemented
    def _geta(self, key, nocheck=False): pass

    @unimplemented
    def _deleteall(self): pass

    @unimplemented
    def _deletea(self, key, nocheck=False): pass

    @unimplemented
    def _puta(self, key, val, nocheck=False): pass

    @unimplemented
    def index(self): pass

    def _open(self): pass

    def _flush(self): pass

    def _close(self): pass

    def setup_defaults(self): return {}


class PickleBackend(BaseBackend):
    __fileext__ = '.pickle'
    __defaults__ = {
    'keys': [],
    'data': {}
    }
    __autoflush__ = True

    def _flush(self):
        self._writef(pickle.dumps(self.db))

    def _open(self):
        if self.dbfile is None:
            self.dbfile = self._fpath() + self.__fileext__
        if self.db is None:
            if not fs.isfile(self.dbfile):
                self.db = {}
                self.setup_defaults()
                self._flush
            else:
                self.db = pickle.loads(self._readdf())

    def _readdf(self):
        fdb = open(self.dbfile, 'rb')
        data = fdb.read()
        fdb.close()
        return data

    def _writef(self, data):
        fdb = open(self.dbfile, 'wb')
        fdb.write(data)
        fdb.close()

    def setup_defaults(self):
        for k in self.__defaults__.keys():
            self.db[k] = self.__defaults__[k]

    def _a2i(self, key):
        tkey = type(key)
        if tkey in [str, unicode]:
            if key not in self.db['keys']:
                raise KeyError('Key %s does not exist in our database.' % key)
            for i, k in enumerate(self.db['keys']):
                if k == key: return i
            return -1
        elif tkey in [long, int]:
            return int(key)
        else:
            raise KeyError('Don\'t know what to do with type of key: %s' % str(tkey))

    def _getrange(self, start=None, stop=None):
        if start is not None:
            start = self._a2i(start)
        else:
            start = 0
        if stop is not None:
            stop = self._a2i(stop)
        else:
            stop = len(self.db['keys'])
        if start < 0 or stop > len(self.db['keys']) or start > stop:
            raise Exception('Indexes specified are out of range of possible values.')
        for k in self.db['keys'][start:stop]:
            yield k, self.db['data'][k]

    def keys(self):
        for k in self.db['keys']:
            yield k

    def _i2a(self, index):
        return self.db['keys'][index]

    def _geta(self, key, nocheck=False):
        key = str(key)
        if not nocheck: _validate_key(key)
        return None if not self.has(key) else self.db['data'][key]

    def _deleteall(self):
        self.setup_defaults()

    def has(self, key):
        return key in self.db['keys']

    def _puta(self, key, val, nocheck=False):
        key = str(key)
        if not nocheck: _validate_key(key)
        exists = self.has(key)
        self.db['data'][key] = val
        if not exists:
            self.db['keys'].append(key)
        if self.__autoflush__:
            self.flush()

    def index(self, increment=False):
        return len(self.db['keys']) + 1

    def _deletea(self, key, nocheck=False):
        if key in self.db['keys']:
            self.db['keys'].remove(key)
        if self.db['data'].has_key(key):
            del self.db['data'][key]


@dbbackend()
def _backend_pickle():
    return PickleBackend


@dbbackend()
def _backend_snappy(snappy='clib.snappy'):
    class SnappyBackend(PickleBackend):
        __fileext__ = '.snappy'

        def _readdf(self):
            return snappy.loadf(self.dbfile)

        def _writef(self, data):
            snappy.savef(self.dbfile, data)

    return SnappyBackend


@dbbackend()
def _backend_sqlite3(sqlite3): pass


@dbbackend()
def _backend_leveldb(leveldb):
    class LevelDBBackend(BaseBackend):
        __defaults__ = {
        '#index': 1L
        }

        def _open(self):
            if self.dbfile is None:
                self.dbfile = self._fpath()
            if self.db is None:
                self.db = leveldb.LevelDB(self.dbfile)
            if not self.has('#index'):
                self.setup_defaults()

        def setup_defaults(self):
            for k in self.__defaults__.keys():
                self.db.Put(k, pickle.dumps(self.__defaults__[k]))

        def _getrange(self, start=None, stop=None):
            for key, val in self.db.RangeIter(key_from=start, key_to=stop):
                if not key.startswith('#') and not key.startswith('@'):
                    yield key, pickle.loads(val)

        def keys(self):
            for key in self.db.RangeIter(include_value=False):
                if not key.startswith('#') and not key.startswith('@'):
                    yield key

        def _i2a(self, index):
            key = '@%d' % long(index)
            return self.db.Get(key)

        def _geta(self, key, nocheck=False):
            key = str(key)
            try: result = self.db.Get(key)
            except KeyError:
                return None
            return pickle.loads(result)

        def _deleteall(self):
            del self.db
            self.db = None
            leveldb.DestroyDB(self.dbfile)
            self._open()

        def _puta(self, key, val, nocheck=False):
            key = str(key)
            if not nocheck: _validate_key(key)
            exists = self.has(key)
            self.db.Put(key, pickle.dumps(val))
            if not exists:
                i = '@%d' % self.index(True)
                self.db.Put(i, key)

        def index(self, increment=False):
            result = self._geta('#index', True)
            if increment:
                self._puta('#index', result + 1L, True)
            return result

        def _deletea(self, key, nocheck=False):
            key = str(key)
            self.db.Delete(key)

    return LevelDBBackend


def get_db_backend(data_dir, dbname, backend='pickle'):
    backend = backends[backend] if backends.has_key(backend) else backends['pickle']
    if id(backend) == id(get_db_backend):
        raise Exception('We seem to missing dependencies on your desired backend, %s' % backend)
    return backend(data_dir, dbname)

