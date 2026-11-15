#!/usr/bin/env python3
import os,json,pathlib,hashlib,secrets,urllib.request,urllib.error,http.cookies
b=os.environ['BASE_URL'].rstrip('/');phase=os.environ['SMOKE_PHASE'];assert phase in ('boot','upgrade','redeploy');p=pathlib.Path(__file__).with_name('state-'+hashlib.sha256(b.encode()).hexdigest()[:16]+'.json');cookie=''
def req(path,data=None,expected=(200,),method=None,bearer=None):
 global cookie
 headers={'Content-Type':'application/json'}
 if cookie:headers['Cookie']=cookie
 if bearer:headers['Authorization']='Bearer '+bearer
 q=urllib.request.Request(b+path,headers=headers,data=None if data is None else json.dumps(data).encode(),method=method)
 try:r=urllib.request.urlopen(q,timeout=40)
 except urllib.error.HTTPError as e:r=e
 with r:status=r.code;raw=r.read();setcookie=r.headers.get('Set-Cookie')
 assert status in expected,f'{path}: status {status}'
 if setcookie:
  jar=http.cookies.SimpleCookie();jar.load(setcookie);cookie='; '.join(k+'='+v.value for k,v in jar.items())
 return json.loads(raw) if raw else None
req('/api/v1/projects',expected=(401,))
req('/api/v1/auth/login',{'username':os.environ.get('ADMIN_USER','admin'),'password':'wrong-'+os.environ['ADMIN_PASSWORD']},expected=(401,))
assert req('/api/v1/auth/login',{'username':os.environ.get('ADMIN_USER','admin'),'password':os.environ['ADMIN_PASSWORD']})['authenticated'] is True
assert cookie,'admin session cookie missing'
req('/api/v1/events',{'title':'invalid credential probe'},expected=(401,),bearer='boop_proj_invalid')
if p.exists():s=json.loads(p.read_text())
else:
 assert phase=='boot','missing boot state; never recreate persisted records'
 title='railway-'+secrets.token_hex(10);project=req('/api/v1/projects',{'name':title},expected=(201,));pid=project['id'];key=project['api_key']
 req('/api/v1/projects/'+pid,{'notify':False},method='PATCH')
 event=req('/api/v1/events',{'title':title},expected=(201,),bearer=key);s={'project':pid,'event':event['id'],'title':title}
 p.write_text(json.dumps(s));p.chmod(0o600)
project=req('/api/v1/projects/'+s['project']);event=req('/api/v1/events/'+s['event']);assert project['name']==s['title'];assert event['title']==s['title'] and event['project_id']==s['project']
print(json.dumps({'ok':True,'phase':phase,'project_and_event_persisted':True,'negative_admin_and_ingest_auth':True,'external_push_tested':False}))
