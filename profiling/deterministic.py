"""
"""

import _lsprof
import collections
import functools
import importlib
import inspect
import os

try:
    thread = importlib.import_module('thread')
except ImportError:
    try:
        thread = importlib.import_module('_thread')
    except ImportError:
        try:
            thread = importlib.import_module('dummy_thread')
        except ImportError:
            thread = importlib.import_module('_dummy_thread')

# def _fullname(function):
#     def traverse(obj, name):
#         attributes = dir(obj)
#         if name not in attributes:
#             for attr_name in attributes:
#                 if not attr_name.startswith('_'):
#                     attr = getattr(obj, attr_name)
#                     if inspect.isclass(attr):
#                         subpath = traverse(attr, name)
#                         if subpath:
#                             return [attr_name] + subpath
#         else:
#             return [name]
#         return []
#     module = inspect.getmodule(function)
#     function_name = function.__name__
#     if module:
#         subpath = traverse(module, function_name)
#         if not subpath:
#             subpath = [function_name]
#         return '.'.join([module.__name__] + subpath)
#     else:
#         return '.'.join(['None', function_name])


class VoidProfiler(object):
    """Pass trough profiler.

    Convenience class that simply does not profile. Implements
    :py:class:`_lsprof.Profiler` and :py:class:`BasicProfiler` interfaces, but
    actually does nothing.

    >>> import time
    >>> from profiling import deterministic
    >>>
    >>> profile = deterministic.VoidProfiler()
    >>> with profile.enabled():
    ...     time.sleep(2)
    >>> profile.getstats()
    []
    >>>
    """

    class _nullContextManager(object):
        def __enter__(context):
            return None

        def __exit__(context, type_, value, traceback):
            return None

    def enabled(self, *args, **kwargs):
        return self._nullContextManager()

    def enable(self, *args, **kwargs):
        return None

    def disable(self):
        return None

    def getstats(self):
        return list()

    def clear(self):
        return None

    def __call__(self, *args, **kwargs):
        return lambda f: f

    def collect():
        return {None: []}


class BasicProfiler(object):
    def enabled(self, *args, **kwargs):
        """Returns Context manager.

        Arguments are passd to :py:meth:`CallProfiler.enable`.

        >>> from profiling import deterministic
        >>>
        >>> profile = deterministic.CallProfiler()
        >>>
        >>> with profile.enabled(builtins=False):
        ...     time.sleep(1.0)
        ...
        """
        class _contextManager(object):
            def __enter__(context):
                self.enable(*args, **kwargs)

            def __exit__(context, type_, value, traceback):
                self.disable()

        return _contextManager()

    def __call__(self, *e_args, **e_kwargs):
        """Function decorator.

        Arguments are passd to :py:meth:`CallProfiler.enable`.

        >>> from profiling import deterministic
        >>>
        >>> profile = deterministic.CallProfiler()
        >>>
        >>> @profile(subcalls=False)
        ... def heavy_duty(arg1, arg2=Null, *args, **kwargs):
        ...     time.sleep(5.0)
        ...
        """
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*f_args, **f_kwargs):
                with self.enabled(*e_args, **e_kwargs):
                    return f(*f_args, **f_kwargs)
            return wrapper
        return decorator

    def collect(self):
        """Collects and clears data in :py:class:`CallProfiler`."""
        self.disable()
        colleted = self.getstats()
        self.clear()
        return {self.__class__: (None, colleted)}


class BasicDeterministicProfiler(_lsprof.Profiler, BasicProfiler):
    """Basic deterministic profiler.

    The objective of this class is to provide a fairly easy interface
    (:py:class:`BasicProfiler`) to the python deterministic profiler
    (:py:class:`_lsprof.Profiler`).
    """



class BasicTimeProfiler(BasicProfiler):
    """Basic time profiler.

    This profiler just measure the elapsed time using :py:func:`os.times`.
    """

    Entry = collections.namedtuple('Entry',
                                   ['user_time', 'system_time',
                                    'children_user_time',
                                    'children_system_time',
                                    'real_time'])

    def __init__(self, *args, **kwargs):
        self.clear()
        self._times = None

    def enable(self, *args, **kwargs):
        self._times = os.times()

    def disable(self):
        if self._times is not None:
            begin, self._times = self._times, None
            entry = self.Entry(*[e - b for e, b in zip(os.times(), begin)])
            self._stats.append(entry)
        
    def getstats(self):
        return list(self._stats)

    def clear(self):
        self._stats = collections.deque()


class DeterministicProfiler(object):

    PROFILE = os.environ.get('CALL_PROFILE', 'TRUE').upper() == 'TRUE'
    MAX_PROFILES = int(os.environ.get('MAX_PROFILES', '50'))

    def __init__(self, profiler_class=VoidProfiler, *args, **kwargs):
        self._profiler_class = profiler_class
        self._stats = dict()
        profiler_factory = lambda: profiler_class(*args, **kwargs)
        self._profiler = collections.defaultdict(profiler_factory)
        self._stack_depth = collections.defaultdict(int)
        self._collecting = thread.allocate_lock()
        self._void_profiler = VoidProfiler()

    def __call__(self, max_profiles=None, *e_args, **e_kwargs):
        """Callable decorator.

        >>> profile = CallProfiler()
        >>>
        >>> @profile(subcalls=False, builtins=False)
        >>> def f():
        ...     pass
        ...
        """
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*f_args, **f_kwargs):
                this_thread = thread.get_ident()
                self._stack_depth[this_thread] += 1
                try:
                    if self.PROFILE and self._stack_depth[this_thread] == 1:
                        profiler = self._profiler[this_thread]
                        with profiler.enabled(*e_args, **e_kwargs):
                            return f(*f_args, **f_kwargs)
                    else:
                        profiler = self._void_profiler
                        return f(*f_args, **f_kwargs)
                finally:
                    self._stack_depth[this_thread] -= 1
                    collected = profiler.getstats()
                    if collected:
                        profiler.claer()
                        with self._collecting:
                            try:
                                stats = self._stats[f_name]
                            except KeyError:
                                deque = collections.deque(maxlen=max_profiles)
                                stats = self._stats[f_name] = deque
                            stats.append(collected)
            return wrapper
        return decorator

    def collect(self):
        with self._collecting:
            collected, self._stats = self._stats, dict()
        return (self.profiler_class, tuple(collected.items()))


def collect(profiler):

    def label(code):
        if isinstance(code, str):
            # built-in functions ('~' sorts at the end)
            return ('~', 0, code)
        else:
            return (code.co_filename, code.co_firstlineno, code.co_name)
    
    profiler_class , collected_items = profiler.collect()
    for function, entries in collected_items:
        callersdicts = {}
        # call information
        for entry in entries:
            name = label(entry.code)
            nc = entry.callcount         # ncalls column of pstats (before '/')
            cc = nc - entry.reccallcount # ncalls column of pstats (after '/')
            tt = entry.inlinetime        # tottime column of pstats
            ct = entry.totaltime         # cumtime column of pstats
            callersdicts[id(entry.code)] = callers = {}
            stats[name] = cc, nc, tt, ct, callers
        # subcall information
        for entry in entries:
            if entry.calls:
                name = label(entry.code)
                for subentry in entry.calls:
                    try:
                        callers = callersdicts[id(subentry.code)]
                    except KeyError:
                        continue
                    nc = subentry.callcount
                    cc = nc - subentry.reccallcount
                    tt = subentry.inlinetime
                    ct = subentry.totaltime
                    if name in callers:
                        prev = callers[name]
                        nc += prev[0]
                        cc += prev[1]
                        tt += prev[2]
                        ct += prev[3]
                    callers[name] = nc, cc, tt, ct
