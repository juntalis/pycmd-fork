def pyglobals():
    pp = __import__('pprint')
    pp = pp.pprint

    def ppd(*args):
        for arg in args:
            pp(arg)

    return {
    'PyCmd': __import__('__main__'),
    'pprint': pp,
    'dprint': ppd
    }

globs = pyglobals()

def cmd_py(args):
    global globs
    if len(args) == 0:
        code = __import__('code')
        con = code.InteractiveConsole(locals=globs)
        con.interact('PyCmd Internal Interpreter')
        return None
    for arg in args: eval(arg, globs)
    return None


def cmd_echo(args):
    print "Echo from Python"
    print args
    return None


def cmd_getenv(args):
    os = __import__('os')
    result = None
    if len(args) == 1:
        args = args[0]
        if os.environ.has_key(args):
            result = os.environ[args]
        else:
            print 'No environment variable with the name, "%s"' % args
    else:
        for arg in args:
            if not os.environ.has_key(arg):
                print 'No environment variable with the name, "%s"' % arg
                result = None
                break
            if result is None:
                result = '%s=%s' % (arg, os.environ[arg])
            else:
                result += '\n%s=%s' % (arg, os.environ[arg])
    if result is not None:
        print result
    return None
