import json
import subprocess
import sys
from datetime import datetime
import argparse

today = datetime.today().strftime('%Y-%m-%d')

parser = argparse.ArgumentParser()
parser.add_argument('--system', type=str, default='x86_64-linux')
parser.add_argument('--compiler', type=str, default='0.15.7')
parser.add_argument('--published', type=str, default=today)
args = parser.parse_args()

with open("flake.lock", "r") as f:
    lockfile = json.load(f)
locked = lockfile['nodes']['purenix-base']['locked']
repo = f'https://github.com/{locked["owner"]}/{locked["repo"]}.git'
ref = locked["rev"]
result = subprocess.Popen(["nix", "eval", f".#drvs.{args.system}", "--json"], stdout=subprocess.PIPE).stdout.read()
package_set = json.loads(result)
derivations = list(p['drvPath'] for p in package_set.values())
build_results = subprocess.Popen(["nix-build-results"] + derivations, stdout=subprocess.PIPE).stdout.read()
res = json.loads(build_results)
with open('results.json', 'w') as f:
    print(json.dumps(res), file=f)
def update_version(name, value, subdir):
    if value['isLocal'] == True:
        return value | {'version': {'git': repo, 'ref': ref, 'subdir': subdir}}
    else:
        return value
named = {k: res[v['drvPath']] | {"derivation": update_version(k, v, f'purescript-{k}')} for k, v in package_set.items()}
final = {k: v['derivation']['version'] for k, v in named.items() if v['success'] == True}
output = {
    'packages': final,
    'compiler': args.compiler,
    'published': args.published,
}
print(json.dumps(output))
