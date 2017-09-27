import json
from multiprocessing import Lock, RawValue
import sys
import time
import traceback

import falcon

import numpy as np
import pandas as pd
import pyarrow as pa


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            df = obj.astype(object).where(pd.notnull(obj), None)
            result = df.to_dict('records')
        elif isinstance(obj, np.generic):
            # numpy types to python internal
            result = np.asscalar(obj)
        else:
            result = json.JSONEncoder.default(self, obj)
        return result

class MyDataObject():

    __slots__ = ('__result', '__value')

    def __init__(self, value):
        self.__value = value
        self.__result = None

    @property
    def value(self):
        return self.__value

    def setResult(self, value):
        self.__result = value

    @property
    def result(self):
        return self.__result

    def __str__(self):
        return "%s %s" % (self.__value, self.__result)

class ScriptRunner():
    _count = 0
    _engine = None
    _lock = None

    _containerType = MyDataObject

    def __init__(self, engine):
        self._count = RawValue('i', 0)
        self._engine = engine
        self._lock = Lock()

    def _getId(self):
        with self._lock:
            result = self._count.value
            self._count.value = result + 1

        return result

    def _assembleArgs(self, req):
        # v = pd.Series(req.params.get('v', []), name='_')
        # p = pd.Series(req.params.get('p', []), dtype=float, name='p')
        # return pd.DataFrame({'_': v, 'p': p})

        v = req.get_param_as_list('v', required=False)
        p = req.get_param_as_list('p', required=False)

        if len(p) > len(v):
            p = p[0:len(v)]
        elif len(p) < len(v):
            p += (len(v) - len(p)) * [None, ]

        data = [
            pa.array(v),
            # TODO: Float16 Array not implemented as of pyarrow 0.7
            # pa.array(req.params.get('p', []), type=pa.float16()),
            pa.array(np.array(p, dtype=np.float))
        ]
        df = pa.RecordBatch.from_arrays(data, ['_', 'p'])

        return df.to_pandas()

    def on_get(self, req, resp, key):
        start = time.time()

        debug = req.get_param('_debug', required=False, default=False)
        runtime = {}
        result = {
                  'id': self._getId(),
                  'wrapper': 'run',
                  'executor': self._engine.executor,
                  'script': key,
                  'runtime': runtime,
                 }

        try:
            df = self._assembleArgs(req)
            argContainer = self._containerType(df)
            if debug:
                result['args'] = df.to_dict('records')
            args = {'x': argContainer}
        except Exception as ex:
            args = None
            resp.code = falcon.HTTP_BAD_REQUEST
            if debug:
                result['exception'] = 'pre-processing failed: %s\n%s' % (ex, traceback.format_exception(*sys.exc_info()))
            else:
                result['exception'] = str(ex)

        runtime['prep'] = int((time.time() - start) * 1000000)

        if args is not None:
            try:
                startExec = time.time()
                self._engine.execute(key, env=args, limit=None)
                runtime['exec'] = int((time.time() - startExec) * 1000000)
                result['result'] = args['x'].result
                resp.code = falcon.HTTP_OK

            except KeyError:
                resp.code = falcon.HTTP_NOT_FOUND

            except Exception as ex:
                resp.code = falcon.HTTP_BAD_REQUEST
                result['exception'] = 'execution failed: %s' % (ex,)

        runtime['overall'] = int((time.time() - start) * 1000000)
        resp.body = json.dumps(result, cls=ExtendedJSONEncoder)
