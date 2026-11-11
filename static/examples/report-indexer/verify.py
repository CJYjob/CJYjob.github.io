"""Verify sample extraction against predeclared expected facts."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).parent
subprocess.run([sys.executable,'-I',str(ROOT/'make_samples.py')],check=True)
spec=importlib.util.spec_from_file_location('indexer',ROOT/'report_indexer.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
result=m.collect(ROOT/'samples','2026-10')
assert len(result['documents'])==2, result
assert result['people']['Researcher-A']==dict(reports=2,projects=['Project-Example']),result
assert result['people']['Researcher-B']['reports']==1,result
assert result['documents'][0]['vulnerabilities']==['Sample-XSS'],result
assert not result['errors'],result
all_rows=m.collect(ROOT/'samples',None)
assert len(all_rows['documents'])==3,all_rows
# Invalid metadata must not be silently treated as a valid report.
from zipfile import ZipFile
from tempfile import TemporaryDirectory
with TemporaryDirectory() as tmp:
    with ZipFile(Path(tmp)/'invalid.docx','w') as z:z.writestr('word/document.xml','<doc/>')
    invalid=m.collect(Path(tmp),None)
    assert len(invalid['errors'])==1 and not invalid['documents'],invalid
summary=dict(tests='PASS',month_documents=2,all_documents=3,people=result['people'],invalid_metadata='reported')
(ROOT/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
