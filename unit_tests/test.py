from mygit.utils import *

test = "find_repo"
test = "get_relative_absolute_paths"
match test:
    case "find_repo":
        print(find_repo("./"))
        
    case "get_relative_absolute_paths":
        get_relative_absolute_paths(["./", "~/Sam/mygit_project/test/f0/4.txt"])