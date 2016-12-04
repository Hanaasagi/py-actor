# -*-coding:UTF-8-*-

import uuid
import multiprocessing


class ActorDeadError(Exception):

    '''
        This Exception will raise when use a dead or unavailable actor.
    '''
    pass


class Actor(object):
    '''
        Actor Base Class
    '''
    actor_urn = None

    actor_mailbox = None

    actor_stopped = None

    actor_ref = None

    def __init__(self, *args, **kwargs):
        self.actor_urn = uuid.uuid4().urn
        self.actor_mailbox = self._create_mailbox()
        self.actor_stopped = multiprocessing.Event()
        self.actor_ref = ActorRef(self)

    @classmethod
    def start(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        obj._start_actor_loop()
        return obj.actor_ref

    @staticmethod
    def _create_mailbox():
        raise NotImplementedError()

    @staticmethod
    def _create_future():
        raise NotImplementedError()

    @staticmethod
    def _start_actor_loop():
        raise NotImplementedError()

    def __str__(self):
        return '{self.__class__.__name__} {self.actor_urn}'.format(self=self)

    def stop(self):
        self.actor_ref.send({'command': '_PYACTOR_STOP'})

    def _stop(self):
        self.actor_stopped.set()

    def _loop(self):
        while not self.actor_stopped.is_set():
            message = self.actor_mailbox.get()
            future = None
            try:
                # get the reply_to future
                future = message.pop('_PYACTOR_REPLY_TO', None)
                result = self._handle_recive(message)
                if future:
                    future.set(result)
            except Exception:
                if future:
                    future.set_exception()
                else:
                    self.actor_stopped.set()

        while not self.actor_mailbox.empty():
            message = self.actor_mailbox.get()
            future = message.pop('_PYACTOR_REPLY_TO', None)
            if future:
                if message.get('command') == '_PYACTOR_STOP':
                    future.set(None)
                else:
                    future.set_exception(ActorDeadError(
                        '{} has stopped'.format(self.actor_ref)))

    def _handle_recive(self, message):
        if message.get('command') == '_PYACTOR_STOP':
            return self._stop()
        return self.on_receive(message)

    def on_receive(self, message):
        raise NotImplementedError()


class ActorRef(object):

    actor_class = None
    actor_urn = None
    actor_mailbox = None
    actor_stopped = None

    def __init__(self, actor):
        self._actor = actor
        self.actor_class = actor.__class__
        self.actor_urn = actor.actor_urn
        self.actor_mailbox = actor.actor_mailbox
        self.actor_stopped = actor.actor_stopped

    def __repr__(self):
        return '<ActorRef for {}>'.format(self)

    def __str__(self):
        return '{self.__class__.__name__} {self.actor_urn}'.format(self=self)

    def is_alive(self):
        return not self.actor_stopped.is_set()

    def send(self, message):
        if not self.is_alive():
            raise ActorDeadError('{} not found'.format(self))
        self.actor_mailbox.put(message)

    def ask(self, message):
        future = self.actor_class._create_future()
        message['_PYACTOR_REPLY_TO'] = future
        try:
            self.send(message)
        except ActorDeadError:
            future.set_exception(ActorDeadError('Unavailable Actor'))
        return future

    def stop(self, block=True, timeout=None):
        ask_future = self.ask({'command': '_PYACTOR_STOP'})

        def _stop_result_converter(timeout):
            try:
                ask_future.get(timeout=timeout)
                return True
            except ActorDeadError:
                return False

        converted_future = ask_future.__class__()
        converted_future.set_trigger(_stop_result_converter)

        if block:
            return converted_future.get(timeout=timeout)
        else:
            return converted_future
