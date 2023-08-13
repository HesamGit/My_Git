import argparse

def get_parser():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='command', metavar='command')
    sub_parsers.required = True

    git_init_parser = sub_parsers.add_parser('init', help='initialize git repo')
    git_init_parser.add_argument('paths', nargs=1, metavar='path', help='folder path to make repo in')

    git_rm_parser = sub_parsers.add_parser('rm', help='rm file(s) from index')
    git_rm_parser.add_argument('paths', nargs='+', metavar='path', help='file or folder paths')

    git_add_parser = sub_parsers.add_parser('add', help='add file(s) to index')
    git_add_parser.add_argument('paths', nargs='+', metavar='path', help='file or folder paths')

    git_commit_parser = sub_parsers.add_parser('commit', help='commit')
    git_commit_parser.add_argument('-a', help='commit author', default="Me")
    git_commit_parser.add_argument('-m', required=True, help='commit message')

    git_checkout_parser = sub_parsers.add_parser('checkout', help='checkout')
    git_checkout_parser.add_argument('commit', help='commit to checkout')

    git_log_parser = sub_parsers.add_parser('log', help='log commits')
    git_log_parser.add_argument('-n', help='number of recent commits', default="5")
    
    git_status_parser = sub_parsers.add_parser('status', help='status')

    args = parser.parse_args()
    return args
