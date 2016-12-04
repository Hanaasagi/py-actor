# -*-coding:UTF-8-*-

import sys
import traceback
import multiprocessing
from pyactor.actor import Actor
from pyactor.future import Future, Timeout
from Queue import Empty


class MultiprocessingActor(Actor):
    '''
        Multiprocessing Actor
    '''
    is_daemon = False

    @staticmethod
    def _create_mailbox():
        return multiprocessing.Manager().Queue()

    @staticmethod
    def _create_future():
        return MultiprocessingFuture()

    def _start_actor_loop(self):
        process = multiprocessing.Process(target=self._loop)
        process.name = process.name.replace('Process', self.__class__.__name__)
        process.daemon = self.is_daemon
        process.start()


class MultiprocessingFuture(Future):

    def __init__(self):
        super(MultiprocessingFuture, self).__init__()
        self._queue = multiprocessing.Manager().Queue(maxsize=1)
        self._data = None

    def get(self, timeout=None):
        try:
            return super(MultiprocessingFuture, self).get(timeout=timeout)
        except NotImplementedError:
            pass

        try:
            if self._data is None:
                self._data = self._queue.get(block=True, timeout=timeout)
            if 'exc_info' in self._data:
                exc_info = self._data.get('exc_info')
                raise exc_info
            else:
                return self._data['value']
        except Empty:
            raise Timeout('%s seconds' % timeout)

    def set(self, value=None):
        self._queue.put({'value': value}, block=False)

    def set_exception(self, exc_info=None):
        if isinstance(exc_info, BaseException):
            exc_info = (exc_info.__class__, exc_info, None)
        if exc_info is None:
            exc_info = sys.exc_info()
        self._queue.put({'exc_info': Exception(
            ''.join(traceback.format_exception(*exc_info)))})
