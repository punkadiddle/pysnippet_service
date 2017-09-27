import sys
import traceback

import falcon

class ScriptManagement():
    
    engine = None
    
    def __init__(self, engine):
        self.engine = engine
    
    def on_get(self, req, resp:falcon.Response, key):
        """Returns the value.
        """
        result = self.engine._scripts.get(key, None)
        if result is None:
            raise falcon.HTTPNotFound()
        else:
            resp.content_type = 'text/plain'
            resp.body = result
            resp.status = falcon.HTTP_200

    def on_put(self, req, resp, key):
        """Set the value.
    
        Returns *True* or *False*.
        """
        try:
            script = req.stream.read().decode()
            self.engine.compile(key, script)
            resp.status = falcon.HTTP_CREATED
            
        except Exception as ex:
            details = traceback.format_exception(*sys.exc_info())
            raise falcon.HTTPBadRequest(str(ex), details)