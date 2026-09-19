import io,json,os,urllib.error
from unittest.mock import patch
import test_local_check as t
a=t.ab_test
key='SYNTHETIC_PREFIX_123456789_SUFFIX'
for include in ['0','1']:
 body='invalid key '+key[:16]+'***'+key[-8:]
 err=urllib.error.HTTPError('http://test.invalid',401,'denied',{},io.BytesIO(body.encode()))
 with patch.dict(os.environ,{a.INCLUDE_BODY_ENV:include}),patch.object(a.urllib.request,'urlopen',side_effect=err):
  try:a.call('http://test.invalid',key,'p',False)
  except SystemExit as e:print(json.dumps({'debug':include,'prefix_visible':key[:16] in str(e),'suffix_visible':key[-8:] in str(e)}))
needle='SYNTHETIC_PRIVATE_CUSTOMER_42'
code,out=t.run_local_check(needle+' x'*100,lambda s:needle,needles=(needle,))
print(json.dumps({'case':'output_privacy','exit':code,'private_needle_visible':needle in out}))
import logging,contextlib
buf=io.StringIO()
root=logging.getLogger(); root.handlers.clear()
logger=logging.getLogger('review.no_handlers');logger.handlers.clear();logger.setLevel(logging.NOTSET)
with contextlib.redirect_stderr(buf):logger.warning('synthetic-warning')
print(json.dumps({'case':'logging_no_handlers','root_handlers':len(root.handlers),'lastResort_present':logging.lastResort is not None,'warning_visible':'synthetic-warning' in buf.getvalue()}))
