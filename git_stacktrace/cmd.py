import argparse
import select
import sys

from git_stacktrace import api


def main():
    usage = "git stacktrace [<options>] [<RANGE>] < stacktrace from stdin"
    description = "Lookup commits related to a given stacktrace"
    parser = argparse.ArgumentParser(usage=usage, description=description)
    range_group = parser.add_mutually_exclusive_group()
    range_group.add_argument('--since', metavar="<date1>", help='show commits '
                             'more recent then a specific date (from git-log)')
    range_group.add_argument('range', nargs='?', help='git commit range to use')
    parser.add_argument('-f', '--fast', action="store_true", help='Speed things up by not running '
                        'pickaxe if cannot find the file')
    args = parser.parse_args()

    if args.since:
        git_range = api.convert_since(args.since)
        print >> sys.stderr, "commit range: %s" % git_range
    else:
        if args.range is None:
            print "Error: Missing range and since, must use one\n"
            parser.print_help()
            sys.exit(1)
        git_range = args.range

    if not api.valid_range(git_range):
        print "Found no commits in '%s'" % git_range
        sys.exit(1)

    if not select.select([sys.stdin], [], [], 0.0)[0]:
        raise Exception("No input found in stdin")
    blob = sys.stdin.readlines()
    traceback = api.Traceback(blob)

    print "Traceback:"
    print traceback

    results = api.lookup_stacktrace(traceback, git_range, fast=args.fast)

    for r in results.get_sorted_results():
        print ""
        print r

    if len(results.get_sorted_results()) == 0:
        print "No matches found"

if __name__ == "__main__":
    main()
