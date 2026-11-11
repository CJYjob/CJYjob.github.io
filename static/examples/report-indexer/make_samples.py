"""Create fictional DOCX fixtures. No company documents are used."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape

def make(name,month,people,project,vulns):
    folder=Path(__file__).parent/'samples';folder.mkdir(exist_ok=True)
    paragraphs=[]
    for style,values in [('ProjectName',[project]),('Performer',people),('VulnHeading',vulns)]:
        for value in values:
            paragraphs.append('<w:p><w:pPr><w:pStyle w:val="'+style+'"/></w:pPr><w:r><w:t>'+escape(value)+'</w:t></w:r></w:p>')
    document='<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+''.join(paragraphs)+'</w:body></w:document>'
    core='<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dcterms:modified xsi:type="dcterms:W3CDTF">2026-'+month+'-15T00:00:00Z</dcterms:modified></cp:coreProperties>'
    types='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>'
    rels='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>'
    with ZipFile(folder/name,'w',ZIP_DEFLATED) as z:
        for path,text in [('word/document.xml',document),('docProps/core.xml',core),('[Content_Types].xml',types),('_rels/.rels',rels)]: z.writestr(path,text)

if __name__=='__main__':
    make('report-a.docx','10',['Researcher-A','Researcher-A','Researcher-B'],'Project-Example',['Sample-XSS','Sample-XSS'])
    make('report-b.docx','10',['Researcher-A'],'Project-Example',['Sample-Upload'])
    make('report-c.docx','09',['Researcher-B'],'Project-Other',['Sample-Auth'])
    print('3 synthetic documents created')
