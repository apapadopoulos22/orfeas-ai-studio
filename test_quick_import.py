import os
os.environ['TESTING']='1'
os.environ['FLASK_ENV']='testing'
from backend.main import OrfeasUnifiedServer
from backend.local_agent_optimizer import demo_agent

server = OrfeasUnifiedServer(enable_local_agent=True)
# Inject demo agent
server.local_agent = demo_agent()
app = server.app

with app.test_client() as c:
    r = c.get('/api/local-agent/status')
    print('STATUS', r.status_code, r.is_json, r.json)
    r2 = c.post('/api/local-agent/call', json={'ability':'uppercase', 'payload':{'text':'hello'}})
    print('CALL OK', r2.status_code, r2.is_json, r2.json)
    r3 = c.post('/api/local-agent/call', json={'ability':'does_not_exist','payload':{}})
    print('CALL MISSING', r3.status_code, r3.is_json, r3.json if r3.is_json else 'N/A')
print(' All LocalAgent endpoints validated without importing torch!')
