__all__ = ['hook_types', 'register_hook', 'unregister_hook', 'get_hooks']

hook_types = ('INIT', 'MAIN', 'TAB',)
pycmd_hooks = {'INIT': {}, 'MAIN': {}, 'TAB': {}}

def register_hook(hook_type, func):
    global pycmd_hooks
    if not hook_type in hook_types:
        print 'Invalid hook_type %s specified for register_hook. Ignored. (function: %s)' % (hook_type, func.__name__)
        return False
    pycmd_hooks[hook_type][func.__name__] = func
    return True


def unregister_hook(hook_type, func):
    global pycmd_hooks
    if not hook_type in hook_types:
        print 'Invalid hook_type %s specified for register_hook. Ignored. (function: %s)' % (hook_type, func.__name__)
        return False
    if not pycmd_hooks[hook_type].has_key(func.__name__): return True
    del pycmd_hooks[hook_type][func.__name__]
    return True


def get_hooks(hook_type=None):
    global pycmd_hooks
    return pycmd_hooks if hook_type is None else pycmd_hooks[hook_type]