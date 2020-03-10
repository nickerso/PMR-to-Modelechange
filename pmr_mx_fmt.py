import json

tmpl = '''<database>
  <name>Physiome Model Repository</name>
  <description>The main goal of the Physiome Model Repository is to provide a resource for the community to store, retrieve, search, reference, and reuse CellML models.</description>
  <release>12</release>
  <release_date>2020-01-01</release_date>
  <entry_count>{entry_count}</entry_count>
  <entries>  
    {entries}
  </entries>
<database>
'''

entry_tmpl = '''
    <entry id="{id}">
      <name>{name}</name>
    </entry>
'''


def convert(stream):
    data = json.load(stream)
    collection_links = data['collection']['links']
    entry_count = len(collection_links)
    entries = [entry_tmpl.format(
        id=entry['href'],
        name=(entry['prompt'] or '').strip(),
    ) for entry in collection_links]
    return tmpl.format(
        entry_count=entry_count,
        entries=''.join(entries),
    )


if __name__ == '__main__':
    import sys
    from os.path import isfile
    from urllib.request import Request, urlopen

    if len(sys.argv) < 2:
        sys.stderr.write('usage: %s <url>\n' % sys.argv[0])
        exit(1)

    if isfile(sys.argv[1]):
        stream = open(sys.argv[1])
    else:
        req = Request(sys.argv[1])
        req.add_header('Accept', 'application/vnd.physiome.pmr2.json.1')
        stream = urlopen(req)

    print(convert(stream))
