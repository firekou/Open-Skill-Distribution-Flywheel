"""Scoped independent checks at d1930e4. Run beside the PR's three Python files."""
import contextlib,io,json,os,subprocess,sys,urllib.error
from unittest.mock import patch
import test_local_check as t
rows=[]
for name,fn,expected in [
 ("shrink",lambda s:"KEEP",0),("unchanged",lambda s:s,3),
 ("equal_rewrite",lambda s:s.replace("x","y"),3),
 ("growth",lambda s:s+"EXTRA",3),("lost",lambda s:"gone",1)]:
 rc,out=t.run_local_check("KEEP "+"x"*200,fn)
 assert rc==expected,(name,rc)
 rows.append({"check":name,"exit":rc,"expected":expected})
key="sk-SYNTHETIC-ONLY-1234567890-ABCDEF"
for body in (key,key[:16]+"***"+key[-8:],key[::-1]):
 err=urllib.error.HTTPError("http://test.invalid",401,"denied",{},io.BytesIO(body.encode()))
 with patch.dict(os.environ,{"ATK_INCLUDE_ERROR_BODY":"1"},clear=True),patch.object(t.ab_test.urllib.request,"urlopen",side_effect=err):
  try:t.ab_test.call("http://test.invalid",key,"prompt",False)
  except SystemExit as e:out=str(e)
 assert body not in out and "401" in out
rows.append({"check":"http_body_full_partial_transformed","withheld":True})
secret="-SYNTHETIC_PRIVATE_42"
for name,args in [
 ("plain_value",["--needlez","SYNTHETIC_PRIVATE_42"]),
 ("dash_value",["--needlez",secret]),
 ("equals_value",["--needlez="+secret])]:
 p=subprocess.run([sys.executable,"local_check.py"]+args,capture_output=True,text=True)
 rows.append({"check":name,"exit":p.returncode,"private_text_visible":"SYNTHETIC_PRIVATE_42" in p.stdout+p.stderr})
assert [r for r in rows if r["check"]=="dash_value"][0]["private_text_visible"]
print(json.dumps(rows,indent=2))
