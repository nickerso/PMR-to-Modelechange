import json
from urllib.request import Request, urlopen
import sqlite3

PMR_INSTANCES = {
    "models": "https://models.physiomeproject.org/",
    "staging": "https://staging.physiomeproject.org/",
    "teaching": "https://teaching.physiomeproject.org/"
}

CACHE_SCHEMA = """
    begin;
    create table exposures (uri text primary key, created timestamp);
    create table exposure_details (exposure text, details text);
    commit;
"""

tmpl = '''<database>
  <name>Physiome Model Repository</name>
  <description>The main goal of the Physiome Model Repository is to provide a resource for the community to store, retrieve, search, reference, and reuse CellML models.</description>
  <contact>help@physiomeproject.org</contact>
  <release>12</release>
  <release_date>2020-01-01</release_date>
  <entry_count>{entry_count}</entry_count>
  <entries>  
    {entries}
  </entries>
</database>
'''

entry_tmpl = '''
    <entry id="{entry_id}">
        <name>{entry_name}</name>
        <description>Description of the model</description>
        <cross_references>
            <ref dbkey="CHEBI:16551" dbname="ChEBI"/>
            <ref dbkey="MTBLC16551" dbname="MetaboLights"/>
            <ref dbkey="CHEBI:16810" dbname="ChEBI"/>
            <ref dbkey="MTBLC16810" dbname="MetaboLights"/>
            <ref dbkey="CHEBI:30031" dbname="ChEBI"/>
        </cross_references>
        <dates>
            <date type="created" value="2013-11-19"/>
            <date type="last_modified" value="2013-11-19"/>
            <date type="submission" value="2020-03-11"/>
            <date type="publication" value="2013-11-26"/>
        </dates>
        <additional_fields>
            <field name="submitter">Andre</field>
            <field name="submitter_mail">d.nickerson@auckland.ac.nz</field>
            <field name="repository">PMR</field>
            <field name="full_dataset_link">{entry_url}</field>
            <field name="omics_type">Models</field>
            <field name="publication"> ... </field>
            <field name="modellingApproach">MAMO term goes here</field>
        </additional_fields>    
    </entry>
'''


def convert(stream):
    data = json.load(stream)
    collection_links = data['collection']['links']
    entry_count = len(collection_links)
    entries = []
    for entry in collection_links:
        url = entry['href']
        # id is being used to construct URL on modeleXchange, so needs to be non-path?
        path = url.replace('https://staging.physiomeproject.org/', '')
        path = path.replace('https://models.physiomeproject.org/', '')
        id = path.replace('/','__')
        raw_name = (entry['prompt'] or 'This model has no name').strip()
        # likely more special characters that might need to be handled?
        name = raw_name.replace('&', '&amp;')
        # req = Request(url)
        # req.add_header('Accept', 'application/vnd.physiome.pmr2.json.1')
        # stream = urlopen(req)
        # entry_data = json.load(stream)
        entries.append(entry_tmpl.format(
            entry_id = id,
            entry_url = url,
            entry_name = name
        ))
    # entries = [entry_tmpl.format(
    #     id=entry['href'],
    #     name=(entry['prompt'] or '').strip(),
    # ) for entry in collection_links]
    return tmpl.format(
        entry_count=entry_count,
        entries=''.join(entries),
    )


if __name__ == '__main__':
    import sys
    from os.path import isfile

    if len(sys.argv) < 3:
        sys.stderr.write('usage: %s <models | staging | teaching> <cache file>\n' % sys.argv[0])
        exit(1)

    base_url = PMR_INSTANCES[sys.argv[1]]
    print('base url = ', base_url)

    cache_file = sys.argv[2]

    db = None
    if not isfile(cache_file):
        db = sqlite3.connect(cache_file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        db.executescript(CACHE_SCHEMA)
    else:
        db = sqlite3.connect(cache_file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

    if isfile(sys.argv[1]):
        stream = open(sys.argv[1])
    else:
        req = Request(sys.argv[1])
        req.add_header('Accept', 'application/vnd.physiome.pmr2.json.1')
        stream = urlopen(req)

    xml = convert(stream)
    print(xml)
    #print(convert(stream))
