import os
import json
import hashlib
import argparse
import datetime as dt

MAX_LEVEL_RECURSION = 10

def print_green(skk): 
    print("\033[92m{}\033[00m".format(skk))
 
def print_yellow(skk): 
    print("\033[93m{}\033[00m".format(skk))

def print_red(skk): 
    print("\033[91m{}\033[00m" .format(skk))

def find_repo(current_folder="./", level=0):    
    abs_path = os.path.abspath(current_folder)
    is_repo_root = ".mygit" in os.listdir(abs_path)
    if is_repo_root:
        return abs_path
    else:
        assert level < MAX_LEVEL_RECURSION and current_folder!="/", "Could not find the repo"
        abs_path = os.path.realpath(os.path.join(abs_path, ".."))
        return find_repo(abs_path, level+1)

def get_absolute_and_relative_paths(paths):
    repo = find_repo()
    abs_rel_paths = []
    for path in paths:             
        abs_path = os.path.realpath(os.path.expanduser(path))
        rel_path = abs_path.split(os.path.realpath(repo) + os.sep)
        if len(rel_path) == 2:
            rel_path = rel_path[1]
        else:
            rel_path = ""
        rel_path = "./" + rel_path        
        abs_rel_paths.append((abs_path, rel_path))
    return abs_rel_paths

def print_index(states):
    print("="*46, " Index ", "="*46)
    print_yellow(json.dumps(states, indent=4))
    print("="*100)

def write_file(*args, content=None):
    path = os.path.join(*args)
    with open(path, "wb") as file:
        file.write(content)

def read_file(*args):
    path = os.path.join(*args)
    with open(path, "r") as file:
        content = file.read()
    return content

def get_datetime():
    return str(dt.datetime.now())

def get_path(hash):
    repo = find_repo()
    path = os.path.join(repo, ".mygit", "objects", hash[:2], hash[2:])
    return path

def hash_obj(data, dtype):
    data_dict = dict(data=data, dtype=dtype)
    sha1 = hashlib.sha1(json.dumps(data_dict, sort_keys=True, indent=4).encode()).hexdigest()
    return sha1

def get_hash_path(path, dtype='file'):
    data = open(path).read()
    return hash_obj(data, dtype=dtype)

def write_hash_obj(data, dtype):
    sha1 = hash_obj(data, dtype)
    data_dict = dict(data=data, dtype=dtype)
    path = get_path(sha1)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data_dict, open(path, "w"), indent=4)
    return sha1

def read_hash_obj(hash, dtype):
    path = get_path(hash)
    try:
        data_dict = json.load(open(path))
    except:
        print(f"Path {path} does not exist for hash {hash}, git object type {dtype}")
    if dtype:
        dtype_from_repo = data_dict["dtype"]
        assert dtype == dtype_from_repo, f"{hash} is not a {dtype} but a {dtype_from_repo}"
    return data_dict["dtype"], data_dict["data"]

def get_file_stat(file):
    stat = os.stat(file)
    keys = ['ctime', 'ctime_ns', 'mtime', 'mtime_ns', 'dev', 'ino', 'mode', 'uid', 'gid', 'size']
    keys = ["st_" + k for k in keys]
    stat_dict = {k: getattr(stat, k) for k in dir(stat) if k in keys}
    return stat_dict

def write_index(states):
    repo = find_repo()
    git_index_path = os.path.join(repo, ".mygit", "index")
    json.dump(states, open(git_index_path, "w"), indent=4)

def read_index():
    repo = find_repo()
    git_index_path = os.path.join(repo, ".mygit", "index")
    states = json.load(open(git_index_path, "r"))
    return states

def get_relative_parent_folder(repo, path):
    f = os.path.realpath(os.path.join(repo, path, "..")).split(repo + os.sep)
    if len(f)==1: 
        f = ""
    else:
        f = f[1]
    f = "./" + f    
    return f

def get_index_folder_map(states):
    repo = find_repo()
    index_folder_map = {}
    for path, state in states.items():
        folder = get_relative_parent_folder(repo, path)        
        index_folder_map[folder] = index_folder_map.get(folder, []) + [state]
    return index_folder_map

def get_hash_folder(path, index=None, folders=None):
    repo = find_repo()
    if path is None:    
        path = repo
    _, path = get_absolute_and_relative_paths([path])[0] # TODO: Do I need this?
    if path not in index:
        return
    if folders is None:
        folders = sorted(index.keys(), key=len, reverse=True)    
       
    for folder in folders: 
        table = {} 
        for state_or_folder in index[folder]:
            # File
            if "path" in state_or_folder: 
                state = state_or_folder
                file = state["path"]  
                sha1 = state["hash"]  
                table[file] = sha1
            
            # Folder
            else:
                folder, sha1 = state_or_folder
                table[folder] = sha1

        sha1 = write_hash_obj(table, dtype="folder")
        parent_folder = get_relative_parent_folder(repo, folder)
        index[parent_folder] =  index[parent_folder] + [(folder, sha1)]
        hash_folder = write_hash_obj(table, dtype="folder")
    return hash_folder

def get_head_commit():
    repo = find_repo()
    commit_hash = read_file(repo, '.mygit', 'refs', 'heads', 'master')
    return commit_hash

def get_active_branch(repo):    
    head = read_file(repo, '.mygit', "HEAD")
    return head.lstrip("ref: refs/heads/"), head

def get_files_folder(hash_folder):
    file_to_hash = {}
    dtype, head_folder = read_hash_obj(hash_folder, "folder")
    for file_folder, hash in head_folder.items():
        dtype, data = read_hash_obj(hash, None)
        if dtype == "file":
            file = file_folder
            file_to_hash[file] = hash
        elif dtype == "folder":
            file_to_hash = {**file_to_hash, **get_files_folder(hash)}
        else:
            raise ValueError(f"Folder should only contain file or folder but it contains {dtype}")
    return file_to_hash

def get_commit_files(hash_head):
    dtype, head_table = read_hash_obj(hash_head, "commit")
    head_top_folder = head_table["top_folder"]
    files = get_files_folder(head_top_folder)
    return files

def is_changed(path, state):
    if get_file_stat(path) != state["stat"]:
        # possibly changed, let's check the hash of contents        
        if get_hash_path(path) != state["hash"]:
            # definitly changed
            return True
    return False

def show_all_git_objects():
    repo = find_repo()
    path = os.path.join(repo, ".mygit", "objects")
    folders = os.listdir(path)
    for folder in folders:
        file_path = os.listdir(os.path.join(path, folder))[0]
        file_path = os.path.join(path, folder, file_path)
        content = open(file_path).read()
        print("\n","="*100)
        print(file_path)
        print(json.loads(content)["dtype"])
        print(content[:150])

def write_file_workdir(path, content):
    with open(path, "w") as file:
        file.write(content)

def construct_folder(table):    
    for work_dir_path, sha1 in table.items():
        dtype, data = read_hash_obj(sha1, None)
        if dtype == "file":
            write_file_workdir(work_dir_path, content=data)
        elif dtype == "folder":
            os.makedirs(work_dir_path, exist_ok=True)
            table_subfolder = data              
            construct_folder(table_subfolder)

def print_commit(commit, hash):
    message, author, datetime = commit["message"], commit["author"], commit["datetime"]
    print(f"\n{author}: {datetime}")
    print(f"{message}")
    print_yellow(f"{hash}")

def skip_file(path_i):    
    flag = path_i.startswith(".git") or path_i.startswith("./.git") or \
        path_i.startswith(".mygit") or path_i.startswith("./.mygit")    
    return flag

def get_workdir_paths(paths, max_level=None):
    if isinstance(paths, str):
        paths = [paths]    
    file_paths = [path for path in paths if not os.path.isdir(path)]
    if max_level == 1:
        for path in paths:
            if skip_file(path): continue
            files = [os.path.join(path, file) for file in os.listdir(path) if "py" not in file]
            file_paths.extend(files)
    else:
        for path in paths:
            for path_i, subdirs, files in os.walk(path):            
                if skip_file(path_i): continue
                for name in files:
                    if "py" in name: continue
                    file_paths.append(os.path.join(path_i, name))
    return file_paths