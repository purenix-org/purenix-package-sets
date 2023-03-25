import json
import subprocess
import sys

with open("flake.lock", "r") as f:
    lockfile = json.load(f)
locked = lockfile['nodes']['purenix-base']['locked']
repo = f'https://github.com/{locked["owner"]}/{locked["repo"]}.git'
ref = locked["rev"]
result = subprocess.Popen(["nix", "eval", ".#hello.x86_64-linux", "--json"], stdout=subprocess.PIPE).stdout.read()
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
final = {k: res[v['drvPath']] | {"derivation": update_version(k, v, f'purescript-{k}')} for k, v in package_set.items()}
print(json.dumps(final))
