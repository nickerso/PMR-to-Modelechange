import argparse
import json
import re
import pathlib
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from git import Repo


PMR_INSTANCES = {
    'models': 'https://models.physiomeproject.org/',
    'teaching': 'https://teaching.physiomeproject.org/',
    'staging': 'https://staging.physiomeproject.org/',
}


def _parse_args():
    parser = argparse.ArgumentParser(prog="workspaces")
    parser.add_argument("--instance", help="PMR instance to work with.",
                        choices=['models', 'teaching', 'staging'], default='models')
    parser.add_argument("--action", choices=['list', 'update'],
                        default='list',
                        help="the action to perform with this instance of PMR.")
    parser.add_argument("--cache", default="pmr-cache",
                        help="Path to the folder to store the local PMR cache in.")
    parser.add_argument("--regex",
                        help='Specify a regex to use in applying the given action to matching workspaces')
    return parser.parse_args()


def get_workspace_list(instance, regex):
    workspace_root = instance + "workspace"
    req = Request(workspace_root)
    req.add_header('Accept', 'application/vnd.physiome.pmr2.json.1')
    stream = urlopen(req)
    data = json.load(stream)
    collection_links = data['collection']['links']
    entry_count = len(collection_links)
    print(f"Total number of workspaces: {entry_count}")
    workspaces = []
    for entry in collection_links:
        if (not regex) or re.match(regex, entry['href']):
            workspaces.append(entry['href'])
    return workspaces


def list_workspaces(workspaces):

    for w in workspaces:
        print(f"Workspace: {w}")
        url = w + "/workspace_view"
        req = Request(url)
        req.add_header('Accept', 'application/vnd.physiome.pmr2.json.1')
        stream = urlopen(req)
        data = json.load(stream)
        print(json.dumps(data, indent=3))
    # entry = collection_links[154]
    # print(entry)
    # url = entry['href']
    # req = Request(url)
    # req.add_header('Accept', 'application/vnd.physiome.pmr2.json.1')
    # stream = urlopen(req)
    # data = json.load(stream)
    # print(json.dumps(data, indent=3))
    # entry = collection_links[908]
    # print(entry)
    # url = entry['href']
    # req = Request(url)
    # req.add_header('Accept', 'application/vnd.physiome.pmr2.json.1')
    # stream = urlopen(req)
    # data = json.load(stream)
    # print(json.dumps(data, indent=3))
    # entries = []
    # for entry in collection_links:
    #     url = entry['href']
    #     #print(url)


def update_workspaces(instance, workspaces, root):
    print(f"Updating the local cache: {root}")
    cache_root = pathlib.Path(root)
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_instance_file = cache_root / ".instance"
    if cache_instance_file.is_file():
        cache_instance = cache_instance_file.read_text()
        if cache_instance != instance:
            print(f"Your local PMR cache originates from {cache_instance}, but {instance} was requested")
            return
    else:
        cache_instance_file.write_text(instance)
    for w in workspaces:
        path = pathlib.Path(urlparse(w).path)
        workspace = path.name
        workspace_cache = cache_root / workspace
        if workspace_cache.exists():
            repo = Repo(workspace_cache)
            repo.remotes.origin.pull()
        else:
            repo = Repo.clone_from(w, workspace_cache)

if __name__ == "__main__":
    args = _parse_args()

    pmr_instance = PMR_INSTANCES[args.instance]
    print(f"PMR Instance: {pmr_instance}")
    workspaces = get_workspace_list(pmr_instance, args.regex)
    print(f"Retrieved {len(workspaces)} workspace(s) from this PMR instance that match the regex: {args.regex}")
    if args.action == 'list':
        list_workspaces(workspaces)
    elif args.action == 'update':
        update_workspaces(pmr_instance, workspaces, args.cache)

    # url = 'https://staging.physiomeproject.org/workspace'
    # print(url)
    # req = Request(url)
    # req.add_header('Accept', 'application/vnd.physiome.pmr2.json.1')
    # stream = urlopen(req)
    # data = json.load(stream)
    # print(json.dumps(data, indent=3))