import logging

import falcon

from script.engine import ScriptEngine
from script.manager import ScriptManagement
from script.runner.attribut import ScriptRunner


# gunicorn --workers 6 script.script:app
# echo "GET http://localhost:8000/run/testRegex?v=fdhghjk&v=c" | $HOME/go/bin/vegeta attack -duration=30s | tee results.bin | $HOME/go/bin/vegeta report
# Requests      [total, rate]            1500, 50.03
# Duration      [total, attack, wait]    29.981178865s, 29.979999841s, 1.179024ms
# Latencies     [mean, 50, 95, 99, max]  2.359393ms, 2.082951ms, 4.230992ms, 5.051949ms, 11.885634ms
# Bytes In      [total, mean]            327929, 218.62
# Bytes Out     [total, mean]            0, 0.00
# Success       [ratio]                  100.00%
# Status Codes  [code:count]             200:1500  
engine =  ScriptEngine()

script1 = '''
if max(x.value['_']) == 27:
    x.setResult(0)
else:
    x.setResult(1)
'''

script2 = '''
while True:
    pass
'''

scriptRegex = '''
result = x.value['_'].str.contains(r'a.*')
x.setResult(result.any())
'''

engine.compile('test1', script1)
engine.compile('test2', script2)
engine.compile('testRegex', scriptRegex)

def app_factory(global_config, **local_conf):
    # configure logging from pastedeploy configuration
    logging.config.fileConfig(global_config['__file__'])
   
    app = falcon.API()
    
    # things will handle all requests to the '/things' URL path
    app.add_route('/script/{key}', ScriptManagement(engine))
    app.add_route('/run/{key}', ScriptRunner(engine))
    
    # falcon.API instances are callable WSGI apps
    return app
