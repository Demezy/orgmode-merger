#!/usr/bin/env python3

import argparse

from nlp import LazyNlp
from org_merger import OrgMerger


def main():
    parser = argparse.ArgumentParser(
        prog='orgmode-merger',
        description='Merge Orgmode files. Delete similar entries.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--disable_nlp',
        action='store_true',
        help='Disable semantical duplicate search',
        required=False,
    )
    parser.add_argument(
        '--headless_policy',
        nargs='?',
        type=str,
        # TODO: add here hint from interactive part
        help='Default choice during interactive part',
    )
    parser.add_argument(
        '-s',
        '--similarity_treshold',
        nargs='?',
        type=float,
        help='treshold to assume that tasks are similar',
        default=0.7,
    )
    parser.add_argument(
        'filenames', nargs='+', help='input orgmode files to merge'
    )
    args = parser.parse_args()

    nlp = LazyNlp('en_core_web_md', treshold=args.similarity_treshold)
    merger = OrgMerger(
        nlp=nlp,
        nlp_enabled=not args.disable_nlp,
        headless_policy=args.headless_policy,
    )
    merged = merger.run(args.filenames)
    print(merged)
    with open('orgmerge_output.org', 'w') as dst:
        dst.write("\n".join(merged))


if __name__ == '__main__':
    main()
