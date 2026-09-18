import contextlib, importlib.util, io, json, pathlib, tempfile, urllib.error
from unittest.mock import patch, MagicMock
HERE=pathlib.Path(__file__).resolve().parent
def load(name):
 s=importlib.util.spec_from_file_location(name,HERE/(name+'.py')); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
m=load('local_check')
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td)/'sample.log'; p.write_text('KEEP '+('x'*200))
 for case, transform in [('shrunk',lambda s:'KEEP'),('unchanged',lambda s:s),('expanded',lambda s:s+'EXTRA'*100),('same_length_changed',lambda s:s.replace('x','y')),('lost',lambda s:'gone')]:
  m.RECEIVED.clear()
  def post(url,prompt,headers):
   m.RECEIVED.append({'messages':[{'role':'user','content':transform(prompt) if headers else prompt}]})
  out=io.StringIO()
  with patch.object(m,'HTTPServer',return_value=MagicMock()), patch.object(m.threading,'Thread',return_value=MagicMock()), patch.object(m.subprocess,'Popen',return_value=MagicMock()), patch.object(m,'wait_for',return_value=True), patch.object(m,'post',side_effect=post), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
   code=m.main(['--log',str(p),'--needle','KEEP'])
  print(json.dumps({'case':case,'exit':code,'output':out.getvalue()}))
a=load('ab_test'); key='SYNTHETIC_REVIEW_KEY_NOT_VALID'
err=urllib.error.HTTPError('http://test.invalid',401,'denied',{},io.BytesIO(json.dumps({'error':'invalid key '+key}).encode()))
with patch.object(a.urllib.request,'urlopen',side_effect=err):
 try:a.call('http://test.invalid',key,'test',False)
 except SystemExit as e:print(json.dumps({'case':'http_error_secret_echo','synthetic_key_visible':key in str(e)}))
