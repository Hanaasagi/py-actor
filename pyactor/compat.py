import sys
import traceback

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    import Queue as queue  # noqa

    string_types = basestring  # noqa

    def reraise(tp, value, tb=None):
        # exec('raise tp, value, tb')
        raise tp, value, tb
        # raise sys.exc_info()

else:
    import queue  # noqa

    string_types = (str,)

    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
