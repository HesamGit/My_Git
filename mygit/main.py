from .parser import get_parser
from .mygit import *

def main():
    args = get_parser()    
    match args.command:
        case "init":
            git_init(args.paths[0])
        case "rm":
            git_rm(args.paths)
        case "add":
            git_add(args.paths)
        case "commit":
            git_commit(args.m, args.a)
        case "checkout":
            git_checkout(args.commit)
        case "log":
            git_log(int(args.n))
        case "status":
            git_status()

if __name__ == "__main__":
    main()