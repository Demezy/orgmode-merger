#!/usr/bin/env python3

import argparse
import random

import orgparse as org
from orgparse.node import OrgNode
from tqdm import tqdm

from nlp import LazyNlp

NLP_ENABLED: bool = True
HEADLESS_POLICY: str | None = None


# display node
def print_content(node: OrgNode):
    print(str(node), f'tags: {node.tags}')


# check are nodes same or not
def are_nodes_same(nlp: LazyNlp, n1: OrgNode, n2: OrgNode) -> bool:
    # speed up by direct comparing
    if n1.heading == n2.heading and n1.body == n2.body:
        return True

    return (
        NLP_ENABLED
        and nlp.is_text_same(n1.heading, n2.heading)
        and nlp.is_text_same(n1.body, n2.body)
    )


def resolve_same_nodes_conflict(n1: OrgNode, n2: OrgNode) -> list[OrgNode]:
    if HEADLESS_POLICY:
        choice = HEADLESS_POLICY
    else:
        print('<<<<<', str(n1), '=====', str(n2), '>>>>>', sep='\n')
        print(
            'These entries seems to be very close. What whould you do?',
            '1) choose first entry',
            '2) choose second entry',
            '3) save both',
            '4) add unique tag to both (manual processing)',
            sep='\n',
        )
        choice = input()
    while choice not in [str(i) for i in range(1, 5)]:
        print('No such option. Try again')
        choice = input()
    if choice == '1':
        return [n1]
    elif choice == '2':
        return [n2]
    elif choice == '3':
        return [n1, n2]
    elif choice == '4':
        tag = 'orgmerge' + str(random.randint(1000000, 10000000))
        n1._tags.append(tag)
        n2._tags.append(tag)
        return [n1, n2]
    return []


# get list of filenames and return merged list of org entries
def merge_files(nlp: LazyNlp, filenames: list[str]) -> list[OrgNode]:
    org_entries: list[OrgNode] = []
    for filename in filenames:
        f = org.load(filename)
        org_entries += f[1:]
    org_entries = list(
        filter(lambda x: x.heading != '' or x.body != '', org_entries)
    )

    # FIXME: this is very inefficient and produce to many dups. As temporal fix
    # set is used, but it breaks original structure => tasks mixed with subtasks!
    merged_entries: set[OrgNode] = set()
    for in1 in tqdm(range(len(org_entries)), desc='Merge progress'):
        for in2 in range(in1 + 1, len(org_entries)):
            n1 = org_entries[in1]
            n2 = org_entries[in2]
            if are_nodes_same(nlp, n1, n2):
                for resolve in resolve_same_nodes_conflict(n1, n2):
                    merged_entries.add(resolve)
                continue
            merged_entries.add(n1)
            merged_entries.add(n2)

    return list(merged_entries)


def run(treshold: float, filenames: list[str]):
    print('ready to go!')
    nlp = LazyNlp('en_core_web_md', treshold=treshold)
    nodes = merge_files(nlp, filenames)
    for n in nodes:
        print_content(n)


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

    global HEADLESS_POLICY, NLP_ENABLED
    HEADLESS_POLICY = args.headless_policy

    if args.disable_nlp:
        NLP_ENABLED = False

    run(args.similarity_treshold, args.filenames)


if __name__ == '__main__':
    main()
