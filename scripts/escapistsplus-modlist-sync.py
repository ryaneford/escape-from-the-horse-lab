#!/usr/bin/env python3
"""Rewrite App.AppSettings.mods on an instance's GenericModule.kvp to an exact
new list, preserving every other field (CustomMission/scenarioId untouched).

Usage: escapistsplus-modlist-sync.py <instance_id> <mods_json_file>
  mods_json_file: JSON list of [modId, name] pairs, in desired load order.
"""
import json, os, re, subprocess, sys, time

INSTANCE_BASE = {
    "eascape0101":  "/home/amp/.ampdata/instances/eascape0101",
    "Escapists201": "/home/amp/.ampdata/instances/Escapists201",
}

def run(cmd):
    print(f"+ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def main():
    instance_id, mods_file = sys.argv[1], sys.argv[2]
    mods = json.load(open(mods_file))
    base = INSTANCE_BASE[instance_id]
    kvp_path = os.path.join(base, "GenericModule.kvp")

    content = open(kvp_path, encoding="utf-8").read()
    idx = content.find('"mods":"')
    start = idx + len('"mods":"')
    end = content.find('","addonsVerify', start)
    if idx == -1 or end == -1:
        print("ABORT: could not locate mods field span")
        sys.exit(1)

    lines = [f'  {{ \\"modId\\": \\"{mid}\\", \\"name\\": \\"{name}\\" }}' for mid, name in mods]
    # NOTE: App.AppSettings=... must stay on a single physical line in the KVP file.
    # Use the literal two-char escape "\n" (backslash + n), never an actual newline byte --
    # a real newline here splits the KVP line and AMP silently regenerates default
    # settings (wiping admins/password/mods/CustomMission) on the next start.
    new_blob = ",\\n\\n".join(lines)
    new_content = content[:start] + new_blob + content[end:]

    if "\n" in new_content[start:start+len(new_blob)]:
        print("ABORT: new_blob contains a literal newline byte, refusing to write")
        sys.exit(1)

    backup = f"{kvp_path}.bak-epxsync-{time.strftime('%Y%m%d-%H%M%S')}"
    run(f"cp -p '{kvp_path}' '{backup}'")
    print(f"{instance_id}: backed up to {backup}")

    run(f"su - amp -c 'ampinstmgr --StopInstance {instance_id}'")
    with open(kvp_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    run("chown -R amp:amp /home/amp/.ampdata/")
    run(f"su - amp -c 'ampinstmgr --StartInstance {instance_id}'")

    time.sleep(5)
    post = open(kvp_path, encoding="utf-8").read()
    post_idx = post.find('"mods":"')
    post_start = post_idx + len('"mods":"')
    post_end = post.find('","addonsVerify', post_start)
    post_blob = post[post_start:post_end]
    post_count = post_blob.count('modId')
    if post_count != len(mods):
        print(f"{instance_id}: WARNING -- after restart, mods count is {post_count}, expected {len(mods)}. "
              f"AMP may have regenerated defaults. Check {kvp_path} and restore from {backup} if needed.")
    else:
        print(f"{instance_id}: wrote {len(mods)} mods, restarted, verified mods count holds post-restart")

if __name__ == "__main__":
    main()
