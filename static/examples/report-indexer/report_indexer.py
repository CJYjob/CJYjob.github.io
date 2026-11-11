"""Independent DOCX style extraction example. Synthetic input only."""
import argparse
import csv
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'dcterms':'http://purl.org/dc/terms/'}

def extract(path):
    with zipfile.ZipFile(path) as z:
        names=['word/document.xml','docProps/core.xml']
        if any(z.getinfo(name).file_size > 2_000_000 for name in names):
            raise ValueError('example size limit exceeded')
        doc=ET.fromstring(z.read(names[0]))
        props=ET.fromstring(z.read(names[1]))
    modified=props.find('dcterms:modified',NS)
    if modified is None or not modified.text:
        raise ValueError('missing modified date')
    date=datetime.fromisoformat(modified.text.replace('Z','+00:00')).date().isoformat()
    fields={'VulnHeading':set(),'Performer':set(),'ProjectName':set()}
    for p in doc.findall('.//w:p',NS):
        style=p.find('w:pPr/w:pStyle',NS)
        if style is None: continue
        name=style.get('{'+NS['w']+'}val')
        if name in fields:
            text=''.join(t.text or '' for t in p.findall('.//w:t',NS)).strip()
            if text: fields[name].add(text)
    if not fields['Performer'] or not fields['ProjectName']:
        raise ValueError('missing performer/project metadata')
    return dict(file=path.name,date=date,vulnerabilities=sorted(fields['VulnHeading']),
                performers=sorted(fields['Performer']),projects=sorted(fields['ProjectName']))

def collect(folder,month):
    rows=[]; errors=[]
    for path in sorted(Path(folder).rglob('*.docx')):
        try:
            row=extract(path)
            if not month or row['date'].startswith(month):
                row['file']=path.relative_to(folder).as_posix();rows.append(row)
        except (ValueError,KeyError,ET.ParseError,zipfile.BadZipFile,OSError) as e:
            errors.append(dict(file=path.relative_to(folder).as_posix(),error=str(e)))
    people={}
    for row in rows:
        for person in row['performers']:
            item=people.setdefault(person,dict(reports=0,projects=set()))
            item['reports']+=1; item['projects'].update(row['projects'])
    summary={p:dict(reports=v['reports'],projects=sorted(v['projects'])) for p,v in sorted(people.items())}
    return dict(documents=rows,people=summary,errors=errors)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('folder',type=Path);parser.add_argument('--month');parser.add_argument('--output',type=Path,default=Path('result'))
    a=parser.parse_args()
    if not a.folder.is_dir(): parser.error('input folder does not exist')
    if a.month and not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])',a.month): parser.error('month must be YYYY-MM')
    result=collect(a.folder,a.month);a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'index.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    with (a.output/'documents.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['file','date','projects','performers','vulnerabilities'])
        for row in result['documents']:w.writerow([row['file'],row['date'],' | '.join(row['projects']),' | '.join(row['performers']),' | '.join(row['vulnerabilities'])])
    print(json.dumps(result,ensure_ascii=False,indent=2))
