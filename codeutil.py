import logging
import miscutil as utility
from collections import namedtuple
from functools import wraps as _wraps

try:
    from llist import dllist, sllist
    remove_index = lambda lst, index: lst.remove(lst.nodeat(index))
except ImportError:
    dllist, sllist = list, list
    remove_index = lambda lst, index: lst.pop(index)

_events = dict()
_patches = dict()
_hijacks = dict()

def _logger():
    """
    Get module-specific logger.
    :return: Module-specific logger
    :rtype: logging.Logger
    """
    return logging.getLogger(__name__)

def _log(level, msg, *args, **kwargs):
    """ Pass-thru to logging.getLogger(...).log """
    return _logger().log(level, msg, *args, **kwargs)

def _critical(msg, *args, **kwargs):
    """ Pass-thru to logging.getLogger(...).critical """
    return _logger().critical(msg, *args, **kwargs)

def _error(msg, *args, **kwargs):
    """ Pass-thru to logging.getLogger(...).error """
    return _logger().error(msg, *args, **kwargs)

def _warn(msg, *args, **kwargs):
    """ Pass-thru to logging.getLogger(...).warn """
    return _logger().warn(msg, *args, **kwargs)

def _info(msg, *args, **kwargs):
    """ Pass-thru to logging.getLogger(...).info """
    return _logger().info(msg, *args, **kwargs)

def _debug(msg, *args, **kwargs):
    """ Pass-thru to logging.getLogger(...).debug """
    return _logger().debug(msg, *args, **kwargs)

def _event_name(name, raise_error=True):
    """
    Verifies that the specified `event` name is valid non-blank string.
    :param name: Event name to validate
    :type name: str | unicode
    :param raise_error: Whether or not to raise errors when invalid
    :type raise_error: bool
    :return: Returns the specified event name on success
    :rtype: str | unicode | None
    :raises TypeError: if name is not an string type instance
    :raises ValueError: if name contains a blank string (empty or whitespace)
    """
    _debug('Verifying event name object: %s', repr(name))
    if isinstance(name, basestring):
        name = name.strip()
        if len(name) > 0:
            return name
        elif not raise_error:
            _debug('Blank event name specified. Returning None.')
            return None
        raise ValueError('Event name cannot be a blank string!')
    elif not raise_error:
        _debug('Non-string event name specified. Returning None.')
        return None
    raise TypeError('Event name must be a string. Received: {0}'.format(
        type(name)
    ))

_HookEventArgs = namedtuple('HookEventArgs', 'data event cancel result handled')

@_wraps(_HookEventArgs)
def HookEventArgs(event, data=None, handled=False, cancel=False, result=None):
    """ Wrapper for construction _HookEventArgs namedtuple with default field
        values. """
    return _HookEventArgs(
        data=data,
        event=event,
        cancel=cancel,
        result=result,
        handled=handled,
    )

def bind(name, handler):
    """
    Bind a handler to a named event.
    :param name: Event name to trigger
    :type name: str | unicode
    :param handler: Handler for event
    :type handler: (*args, **kwargs) -> None
    :return: Nothing yet
    :rtype: None
    :raises TypeError: if name is not an string or handler is not callable
    :raises ValueError: if name contains a blank string (empty or whitespace)
    """
    global _events
    name = _event_name(name)
    if not callable(handler):
        raise TypeError('handler parameter must be callable!')
    elif name not in _events:
        _debug('Constructing new handler list for event: %s', name)
        _events[name] = sllist()

    # Avoid duplicate handlers
    handlers = _events[name]
    if handler not in handlers:
        _debug('Binding handler for "%s" event: %s', name, repr(handler))
        handlers.append(handler)

def unbind(name, handler=None):
    """ Remove a named event handler. If `handler` is None, remove all handlers
        from the named event. If `name` is None, clear all handlers from all
        events. """
    global _events
    if name is None:
        _debug('Removing all event handlers')
        return _events.clear()

    name = _event_name(name)
    handlers = _events.get(name, None)
    if handler is None:
        _debug('Removing all handlers for event: %s', name)
        _events.pop(name, None)
    elif handlers is not None:
        found = -1
        for idx,entry in enumerate(handlers):
            if entry == handler:
                found = idx
                break
        if found != -1:
            _debug('Removing handler for "%s" event: %s', name, repr(handler))
            remove_index(handlers, found)

def trigger(name, eventargs=None, *args, **kwargs):
    """
    Triggers all of the handlers bound to a named event.
    :param name: Event name to trigger
    :type name: str | unicode
    :param args: Event arguments
    :param kwargs: Event keyword arguments
    :return: Event args
    :rtype: HookEventArgs
    :raises TypeError: if name is not an string type instance
    :raises ValueError: if name contains a blank string (empty or whitespace)
    """
    global _events
    name = _event_name(name)
    if eventargs is None:
        eventargs = HookEventArgs(name)

    handlers = _events.get(name, None)
    if handlers is not None:
        eventargs.event = name
        _debug('Triggering handlers for event: %s', name)
        for handler in handlers:
            handler(eventargs, *args, **kwargs)
            if eventargs.handled:
                break

    return eventargs

def triggers(prehook=None, posthook=None):
    """
    Utility decorator for triggering named events before and/or after the
    decorated object. Must specify `prehook`, `posthook`, or both.
    :param prehook: Event triggered before calling the decorated function.
    :type prehook: str | unicode
    :param posthook: Event triggered after calling the decorated function.
    :type posthook: str | unicode
    :raises TypeError: if a specified event name contains a non-string value
    :raises ValueError: if a specified event name is blank
    """
    has_prehook = prehook is not None
    has_posthook = posthook is not None
    def triggers_deco(func):
        @_wraps(func)
        def wrapped(*args, **kwargs):
            eventargs = None
            if has_prehook:
                eventargs = trigger(prehook, None, *args, **kwargs)
                if eventargs.cancel:
                    return eventargs.result

            result = func(*args, **kwargs)
            if has_posthook:
                if has_prehook: eventargs.result = result
                eventargs = trigger(posthook, eventargs, *args, **kwargs)
                result = eventargs.result
            return result

        return wrapped
    return triggers_deco

def patchable(func):
    """ Decorator for potentially hijacking/replacing functions """
    key = utility.membername(func)

    @_wraps(func)
    def wrapped(*args, **kwargs):
        global _patches
        handler = _patches.get(key, func)
        return handler(*args, **kwargs)

    return wrapped

def unpatch(key):
    """
    If a patch was previously installed at `key`, remove it and restore the
    original function. (returns silently if not) Used internally.
    :param key: module.function
    :type key: str | unicode
    """
    global _patches
    if key is None: return
    _patches.pop(key, None)

def patch(key, newfunc):
    """
    Given a function decorated with `patchable`, replace the existing
    implementation with `newfunc`. If `newfunc` is `None`, call `unpatch`
    with the specified `key` parameter. Used internally.
    :param key: module.function
    :type key: str | unicode
    :param newfunc: new function (origfunc, *args, **kwargs) -> result
    :type newfunc: callable | None
    """
    if newfunc is None:
        return unpatch(key)

    global _patches
    if key is None: return
    elif not callable(newfunc):
        raise ValueError('newfunc must be callable!')
    _patches[key] = newfunc

def hijack(key, *args, **kwargs):
    """
    Used internally for cases where I needed to override the behavior
    in the middle of a function's logic or when it wasn't reasonable to
    use the `patchable`/`patch`/`unpatch` system. Dispatcher was used
    instead of direct function calls to alleviate some import issues.
    :param key:
    :type key: str
    """
    global _hijacks
    hijacker = _hijacks.get(key, None)
    if hijacker is None:
        raise IndexError('No code hijack exists with key: {0}'.format(key))
    return hijacker(*args, **kwargs)

def add_hijack(key, func):
    """ Used internally. """
    global _hijacks
    _hijacks[key] = func
