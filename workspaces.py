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


def _request_json(url, debug_print=None):
    req = Request(url)
    req.add_header('Accept', 'application/vnd.physiome.pmr2.json.1')
    req.add_header('User-Agent', 'andre.pmr-utils/0.0')
    data = None
    try:
        stream = urlopen(req)
        data = json.load(stream)
        if debug_print:
            print(f'{debug_print} [get JSON request]: {url}')
            print(json.dumps(data, indent=debug_print))
    except:
        print(f"Requested URL did not return JSON: {url}")

    return data


def _parse_args():
    parser = argparse.ArgumentParser(prog="workspaces")
    parser.add_argument("--instance", help="PMR instance to work with.",
                        choices=['models', 'teaching', 'staging'], default='models')
    parser.add_argument("--action", choices=['list', 'update'],
                        default='list',
                        help="the action to perform with this instance of PMR.")
    parser.add_argument("--cache", default="pmr-cache",
                        help="Path to the folder to store the local PMR cache in.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--regex",
                        help='Specify a regex to use in applying the given action to matching workspaces')
    group.add_argument("-w", "--workspace",
                        help='Specify a single workspace rather than searching PMR')
    return parser.parse_args()


def get_workspace_list(instance, regex, workspace):
    workspace_list = []
    if workspace:
        # user has given a single workspace to use, check its for this instance of PMR
        if not workspace.startswith(instance):
            print(f'The requested workspace, {workspace}, is not from this instance of PMR ({instance}).')
            return workspace_list
        workspace_list.append(workspace)
    else:
        # fetch workspaces from the requested instance
        workspace_root = instance + "workspace"
        data = _request_json(workspace_root)
        collection_links = data['collection']['links']
        entry_count = len(collection_links)
        print(f"Total number of workspaces retrieved: {entry_count}")
        workspace_list = []
        for entry in collection_links:
            if (not regex) or re.match(regex, entry['href']):
                workspace_list.append(entry['href'])
        print(f"Retrieved {len(workspaces)} workspace(s) from this PMR instance that match the regex: {args.regex}")
    return workspace_list


def list_link(link, follow):
    href = link['href']
    prompt = link['prompt']
    rel = link['rel']
    print(f'Link({rel}): {href}; {prompt}')
    if rel == follow:
        data = _request_json(href)
        print(json.dumps(data, indent=2))
        if 'links' in data['collection']:
            for l in data['collection']['links']: list_link(l, follow)
    if rel == 'section':
        data = _request_json(href)
        print(json.dumps(data, indent=5))


def list_exposure(exposure_url):
    print(f'Exposure: {exposure_url}')
    exposure ={
        'href': exposure_url
    }
    data = _request_json(exposure_url, 2)
    exposure_info = data['collection']['items'][0]
    exposure_data = exposure_info['data']
    for d in exposure_data:
        exposure[d['name']] = d['value']
    return exposure

def list_workspace(workspace_url):
    print(f"Workspace: {workspace_url}")
    url = workspace_url + "/workspace_view"
    data = _request_json(url)
    workspace_info = data['collection']['items'][0]
    workspace = {
        'href': workspace_info['href']
    }
    workspace_data = workspace_info['data']
    for d in workspace_data:
        workspace[d['name']] = d['value']
    if 'links' in workspace_info:
        links = workspace_info['links']
        # we only care about the latest exposure, if exists
        for link in links:
            if link['prompt'] == 'Latest Exposure':
                workspace['latest-exposure'] = list_exposure(link['href'])
            else:
                print(f'[list_workspace] Unknown link found and ignored: {link['prompt']}')
    print(json.dumps(workspace, indent=3))


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
    workspaces = get_workspace_list(pmr_instance, args.regex, args.workspace)
    if args.action == 'list':
        for w in workspaces:
            list_workspace(w)

    elif args.action == 'update':
        update_workspaces(pmr_instance, workspaces, args.cache)

    # url = 'https://staging.physiomeproject.org/workspace'
    # print(url)
    # req = Request(url)
    # req.add_header('Accept', 'application/vnd.physiome.pmr2.json.1')
    # stream = urlopen(req)
    # data = json.load(stream)
    # print(json.dumps(data, indent=3))