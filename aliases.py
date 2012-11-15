from userconfig import pycmddb

__all__ = ['get_alias', 'alias_main']

def get_alias(cmd):
    return pycmddb().get(cmd)


def print_usage():
    print 'alias [-h] [-p] [-u] alias_name [cmd]\n'
    print '\t-h\tPrint this help.'
    print '\t-p\tPrint value of alias. If no alias specified, list all.'
    print '\t-u\tUndefine alias_name.\n'
    print 'If no flag is specified, we assume you\'re attempting to set an alias.\n'
    print 'EXAMPLE:\n'
    print '\talias gitcl git clone\n'
    print 'NOTE: Type your cmd just as you would in the console. Do not do the following:\n'
    print '\talias gitcl "git clone"'


def alias_main(args):
    if len(args) == 0:
        print_usage()
    else:
        args[0] = args[0].lower()
        if args[0] == '-?' or args[0] == '-h':
            print_usage()
        elif args[0] == '-p':
            if len(args) == 1:
                i = 0
                for k, v in pycmddb().get():
                    alias = v
                    print u'alias %s=\'%s\'' % (k, alias)
                    i += 1
                if i == 0:
                    print 'No aliases currently defined.'
            elif len(args) == 2:
                alias = args[1]
                aliasobj = pycmddb().get(alias)
                if aliasobj is None:
                    print 'Alias %s not found.' % alias
                else:
                    print u'Alias: %s = %s' % (alias, u' '.join(aliasobj))
            else:
                print_usage()
        elif args[0] == '-u':
            if len(args) == 2:
                alias = args[1]
                aliasobj = pycmddb().get(alias)
                if aliasobj is None:
                    print 'Alias %s not found.' % alias
                else:
                    pycmddb().delete(alias)
                    print 'Alias %s deleted.' % alias
            else:
                print_usage()
        else:
            if len(args) == 1:
                print 'Need a cmd to use.'
            else:
                pycmddb().put(args[0], args[1:])