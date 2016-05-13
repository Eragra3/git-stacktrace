import argparse

from git_stacktrace import parse_trace
from git_stacktrace import git
from git_stacktrace import result


def lookup_file(commit_files, trace_files, results):
    for commit, file_list in commit_files.iteritems():
        for git_file in file_list:
            for f in trace_files:
                if git_file in f:
                    results.get_result(commit).files.add(git_file)


def main():
    usage = "git stacktrace [RANGE] [STACKTRACE FILE]"
    description = "Lookup commits related to a given stacktrace"
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument('range', help='git commit range to use')
    parser.add_argument('stacktrace', help='stacktrace filename')
    args = parser.parse_args()

    extracted = parse_trace.extract_python_traceback_from_file(args.stacktrace)

    parse_trace.print_traceback(extracted)

    trace_files = set()
    trace_snippets = set()
    for f, line, function, code in extracted:
        trace_files.add(f)
        trace_snippets.add(code)

    results = result.Results()

    for snippet in trace_snippets:
        commits = git.pickaxe(snippet, args.range)
        for commit in commits:
            results.get_result(commit).snippets.add(snippet)

    commit_files = git.files_touched(args.range)
    lookup_file(commit_files, trace_files, results)

    for k, v in results.results.iteritems():
        print ""
        git.print_one_commit(k, oneline=True)
        print v

if __name__ == "__main__":
    main()
