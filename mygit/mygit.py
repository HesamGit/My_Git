from .utils import *

def git_init(repo):
    print(f"Initialized empty MyGit repository in {repo}")
    os.makedirs(os.path.join(repo, ".mygit"), exist_ok=True)
    for folder in ["objects", "heads", "refs", "refs/heads", "refs/tags"]:
        os.makedirs(os.path.join(repo, ".mygit", folder), exist_ok=True)
    write_file(repo, '.mygit', 'refs', 'heads', 'master', content=b'')
    write_file(repo, '.mygit', 'HEAD', content=b'ref: refs/heads/master')
    write_index(states={})

def git_rm(paths):
    states = read_index()
    abs_rel_paths = get_absolute_and_relative_paths(paths)
    for abs_path, rel_path in abs_rel_paths:
        if rel_path in states:
            del states[rel_path]
    print_index(states)
    write_index(states)

def git_add(paths):
    file_paths = get_workdir_paths(paths)
    abs_rel_paths = get_absolute_and_relative_paths(file_paths)
    print("MyGit adding files:")
    for _, file_path in abs_rel_paths:
        print_green(f"\t{file_path}")
    states = read_index()    
    for _, path in abs_rel_paths:
        states[path] = {}
        data = open(path).read()
        sha1 = write_hash_obj(data, "file")
        states[path]["stat"] = get_file_stat(path)
        states[path]["hash"] = sha1
        states[path]["path"] = path
    print_index(states)
    write_index(states)
    return states

def git_commit(message, author):
    repo = find_repo()
    datetime = get_datetime()
    states = read_index()
    index_folder_to_state = get_index_folder_map(states)    
    top_folder = get_hash_folder(repo, index=index_folder_to_state)
    parent = get_head_commit()
    commit = dict(author=author, 
                  message=message, 
                  datetime=datetime, 
                  parent=parent,
                  top_folder=top_folder)
    hash = write_hash_obj(data=commit, dtype="commit")    
    branch = get_active_branch(repo)[0]
    if branch:
        write_file(repo, '.mygit', 'refs', 'heads', 'master', content=hash.encode())
    else:
        write_file(repo, '.mygit', 'HEAD', content=hash.encode())
        
    return hash

def git_status():
    repo = find_repo()
    states = read_index()
    index_paths = {path for path in states}
    work_dir_paths = get_workdir_paths(repo)
    relative_work_dir_paths = [x[1] for x in get_absolute_and_relative_paths(work_dir_paths)]
    current_paths = set(relative_work_dir_paths)

    # WorkTree vs Index: Files which exist in current folder but are not in the index are not tracked
    untracked_paths = current_paths - index_paths    

    # WorkTree vs Index: Compare current files and folders with index to find changed files 
    cahnged_paths_not_staged = [path for path in current_paths & index_paths if is_changed(path, states[path])]
    
    # Head vs Index:  Compare git index with head's top folder to find what has really changed     
    branch, head = get_active_branch(repo)    
    hash_head = get_head_commit()
    files_hash_head = get_commit_files(hash_head)
    files_head = set(files_hash_head.keys())
    files_index = set(states.keys())
    cahnged_paths_staged = [path for path in files_index & files_head if is_changed(path, states[path]) and path not in cahnged_paths_not_staged]
    added_paths_staged = files_index - files_head
    del_paths = files_head - files_index    

    if "refs/heads" in head:
        print(f"On branch {branch}.")
    else:
        print(f"HEAD detached at {head}")

    if len(untracked_paths):
        print("Untracked files:")            
        for p in untracked_paths: 
            print_red(f"\t{p}")

    if len(cahnged_paths_not_staged):
        print("Changes not staged for commit:")
        for p in cahnged_paths_not_staged: 
            print_red(f"\t{p}")
    
    if len(del_paths):
        print("Removed files:")    
        for p in del_paths: 
            print_red(f"\t{p}")
    
    if len(cahnged_paths_staged):
        print("Changes to be committed:")
        for p in cahnged_paths_staged: 
            print_green(f"\t{p}")

    if len(added_paths_staged):
        print("Added staged files:")
        for p in added_paths_staged: 
            print_green(f"\t{p}")
    

    return untracked_paths, del_paths, cahnged_paths_not_staged

def git_checkout(commit):
    repo = find_repo()
    dtype, data = read_hash_obj(commit, "commit")    
    top_folder_hash = data["top_folder"]    
    dtype, folder_table = read_hash_obj(top_folder_hash, "folder")
    construct_folder(folder_table)
    branch, head = get_active_branch(repo)
    
    # On active branch's HEAD
    if "refs/heads" in head and read_file(repo, '.mygit', 'refs', 'heads', branch) == commit:         
        # write_file(repo, '.mygit', 'HEAD', content=f'ref: refs/heads/{branch}'.encode())
        pass
    
    # Detached Head
    else:  
        write_file(repo, '.mygit', 'HEAD', content=commit.encode())

def git_log(n):
    hash_commit = get_head_commit()    
    for i in range(n):
        if not hash_commit: 
            break
        dtype, data = read_hash_obj(hash_commit, "commit")
        print_commit(data, hash_commit)
        hash_commit = data["parent"]
