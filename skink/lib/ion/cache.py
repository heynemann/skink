"""Caching dictionary that uses access times to decide which objects to
flush from the cache.

When instantiating, you can set the maximum number of key/value pairs
to maintain in the cache:

    c = Cache(size=1000)

When the maximum size of the cache is reached, it will be resized
automatically to 95% of its maximum size the next time a new key is added to
the dictionary.  The least recently accessed items will be the ones that are
flushed.  A cache size of 0 implies an unlimited size.  (Cache size should
be controlled by an age parameter.)

You can also specify a maximum entry age when creating the cache:

    c = Cache(size=100, age=24*60)    # one hour

By default, entries will remain in the cache until they are bumped for space
or time.  If an attempt is made to retrieve an item that was added to the
cache before the age threshold, ExpiredError is raised (which is a subclass
of KeyError), just as if they weren't present in the cache.

Ages can be specified as numbers of seconds or as strings consisting of a
number followed by one of the following units: d,h,m,s
"""

import time, string, re

class CacheEntry(object):
    __slots__ = ("value", "ftime", "mtime")
    def __init__(self, value):
        self.set(value)
        self.ftime = 0.0

    def get(self):
        self.ftime = time.time()
        return self.value

    def set(self, value):
        self.value = value
        self.mtime = time.time()

class ExpiredError(KeyError):
    pass

class Cache(dict):
    def __init__(self,data=None,size=100,age=None, log=None):
        self.size = size
        self.requests = self.hits = 0
        self.inserts = self.unused = 0
        if isinstance(age, (str, unicode)):
            age = self._cvtage(age)
        self.age = age
        self.log = log

    def shrink(self):
        trim = max(0, int(len(self)-0.95*self.size))
        if trim:
            # sort keys by access times
            values = zip(self.ftimes(), self.keys())
            values.sort()
            for val,k in values[0:trim]:
                if val == 0.0:
                    self.unused += 1
                del self[k]

    def purge_old_entries(self):
        if self.age is None:
            return
        t = time.time()
        for k in self.keys():
            v = dict.__getitem__(self, k)
            threshold = t - self.age
            # modified or fetched in last self.age seconds?
            if threshold > v.mtime and threshold > v.ftime:
                if v.ftime == 0.0:
                    self.unused += 1
                del self[k]

    def __setitem__(self,key,val):
        self.inserts += 1
        if self.age is not None and self.requests % 1000 == 0:
            self.purge_old_entries()

        if (key not in self and self.size and len(self) >= self.size):
            self.shrink()
        dict.__setitem__(self, key, CacheEntry(val))
        if self.log:
            self.log("Setting item %s to %s" % (key, val), "Cache")

    def __getitem__(self,key):
        self.requests += 1
        item = dict.__getitem__(self, key)
        val = item.get()

        if self.age is not None:
            if self.requests % 1000 == 0:
                self.purge_old_entries()

            # check to make sure value has not expired
            if time.time()-self.age > item.mtime:
                if item.ftime == 0.0:
                    self.unused += 1
                del self[key]
                if self.log:
                    self.log("Cache miss at key %s" % key, "Cache")

                raise ExpiredError, key
        
        # if we get here there was no KeyError
        self.hits = self.hits + 1

        if self.log:
            self.log("Cache hit at key %s" % key, "Cache")

        return val

    def has_key(self,key):
        try:
            v = dict.__getitem__(self, key)
        except (KeyError,ExpiredError):
            return 0
        if self.age is not None and time.time()-self.age > v.mtime:
            return 0
        return 1

    def get(self,key,default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def values(self):
        return [dict.__getitem__(self,key).get() for key in self]

    def ftimes(self):
        return [dict.__getitem__(self,key).ftime for key in self]

    def mtimes(self):
        return [dict.__getitem__(self,key).mtime for key in self]

    def items(self):
        return map(None, self.keys(), self.values())

    def copy(self):
        return self.__class__(self, self.size)

    def update(self, dict):
        for k in dict.keys():
            self[k] = dict[k]

    def stats(self):
        return {
            'hits': self.hits,
            'inserts': self.inserts,
            'requests': self.requests,
            'unused': self.unused,
            }

    def __repr__(self):
        l = []
        for k in self.keys():
            l.append("%s: %s" % (repr(k), repr(self[k])))
        return "{" + string.join(l, ", ") + "}"
    __str__=__repr__

    _apat = re.compile("([0-9]+([.][0-9]+)?)\s*([dhms])?\s*$")

    def _cvtage(self,age):
        mat = self._apat.match(age)
        if mat is None:
            raise ValueError, "invalid age spec: "+age
        n = float(mat.group(1))
        units = mat.group(3) or "s"
        if units == "s":
            pass
        elif units == "m":
            n = n * 60
        elif units == "h":
            n = n * 60*60
        elif units == "d":
            n = n * 24*60*60
        return n

