# -*-coding:UTF-8-*-
import sys
import collections
import functools


class Timeout(Exception):

    '''
        Exception raised at future timeout.
    '''
    pass


def _is_iterable(x):
    PY2 = sys.version_info[0] == 2
    PY3 = sys.version_info[0] == 3
    if PY3:
        string_types = (str,)
    if PY2:
        string_types = basestring
    return isinstance(x, collections.Iterable) and \
        not isinstance(x, string_types)


def _map(func, *iterables):
    if len(iterables) == 1 and not _is_iterable(iterables[0]):
        return func(iterables[0])
    else:
        return list(map(func, *iterables))


class Future(object):
    '''
        Future Base Class
    '''

    def __init__(self):
        super(Future, self).__init__()
        self._trigger = None

    def get(self, timeout=None):
        if self._trigger is not None:
            return self._trigger(timeout)
        raise NotImplementedError

    def set(self, value=None):
        raise NotImplementedError

    def set_exception(self, exc_info=None):
        raise NotImplementedError

    def set_trigger(self, func):
        self._trigger = func

    def filter(self, func):
        future = self.__class__()
        future.set_trigger(lambda timeout: list(filter(
            func, self.get(timeout))))
        return future

    def join(self, *futures):
        future = self.__class__()
        future.set_trigger(lambda timeout: [
            f.get(timeout) for f in [self] + list(futures)])
        return future

    def map(self, func):
        future = self.__class__()
        future.set_trigger(lambda timeout: _map(func, self.get(timeout)))
        return future

    def reduce(self, func, *args):
        future = self.__class__()
        future.set_trigger(lambda timeout: functools.reduce(
            func, self.get(timeout), *args))
        return future


def get_all(futures, timeout=None):
    return [future.get(timeout=timeout) for future in futures]
