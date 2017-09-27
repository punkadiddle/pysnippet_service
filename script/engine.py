from contextlib import contextmanager
from hashlib import sha256
import signal
import sys
import time

from RestrictedPython import compile_restricted
from RestrictedPython import safe_builtins


# ContainerAssertions are used by cAccessControl to check access to
# attributes of container types, like dict, list, or string.
# ContainerAssertions maps types to a either a dict, a function, or a
# simple boolean value.  When guarded_getattr checks the type of its
# first argument against ContainerAssertions, and invokes checking
# logic depending on what value it finds.
# If the value for a type is:
#   - a boolean value:
#      - the value determines whether access is allowed
#   - a function (or callable):
#      - The function is called with the name of the attribute and
#        the actual attribute value, then the value is returned.
#        The function can raise an exception.
#   - a dict:
#      - The dict maps attribute names to boolean values or functions.
#        The boolean values behave as above, but the functions do not.
#        The value returned for attribute access is the result of
#        calling the function with the object and the attribute name.
ContainerAssertions = {
    type(()): 1,
    type(''): 1,
    type(u''): 1,
    range: 1,
}

Containers = ContainerAssertions.get

class AccessDenied(Exception):
    pass

DisallowedObject = []
SliceType = type(slice(0))

def guarded_getitem(obj, index):
    if type(index) is SliceType:
        if index.step is not None:
            v = obj[index]
        else:
            start = index.start
            stop = index.stop
            if start is None:
                start = 0
            if stop is None:
                v = obj[start:]
            else:
                v = obj[start:stop]
        # We don't guard slices.
        return v
    v = obj[index]
    if Containers(type(obj)) and Containers(type(v)):
        # Simple type.  Short circuit.
        return v
    if v in DisallowedObject:
        raise AccessDenied('unauthorized access to element %s' % index)
    else:
        return v

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutError()
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

class ScriptEngine(object):
    '''
    classdocs
    '''
    executor = ('%s %s' % ('Restricted Python', sys.version.split('\n')[0])).strip()
    
    repository = None
    _scripts = None
    
    __allowedBuiltins = None

    def __init__(self):
        '''
        Constructor
        '''
        self.repository = dict()
        self._scripts = dict()
        self.__allowedBuiltins = safe_builtins.copy()
        self.__allowedBuiltins['_getitem_'] = guarded_getitem
    
    def _hash(self, name, value):
        result = sha256(value.encode())
        return name.encode() + result.digest()
    
    def compile(self, name, script):
        
        #key = self._hash(name, script)
        key = name
        cacheItem = self.repository.get(key, None)
        if cacheItem is None:
            byteCode = compile_restricted(script, filename=name, mode='exec')
            self.repository[key] = [time.time(), name, byteCode]
            self._scripts[key] = script
        else:
            cacheItem[0] = time.time()
        
        return key
    
    def execute(self, key, env=None, limit=10000):
        
        _, _, code = self.repository[key]
            
        try:
            if limit is None:
                exec(code, self.__allowedBuiltins, env)        
            else:
                with time_limit(limit):
                    exec(code, self.__allowedBuiltins, env)

        except TimeoutError:
            raise
                    
        except Exception as ex:
            lines = self._scripts[key].split('\n')
            tb = sys.exc_info()[2]
            while tb:
                if tb.tb_frame.f_code.co_filename == key:
                    debugText = '\n'.join(['%1s%4d: %s' % ('>' if i+1 == tb.tb_lineno else '',  i+1, lines[i]) for i in range(0,len(lines))])
                    raise RuntimeError('%s, line %d in\n%s' % (ex, tb.tb_lineno, debugText)).with_traceback(tb.tb_next)
                tb = tb.tb_next

    