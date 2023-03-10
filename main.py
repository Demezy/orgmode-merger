#!/usr/bin/env python3

import argparse
import random

import orgparse as org
import spacy
from orgparse.node import OrgNode
from spacy.language import Language
from tqdm import tqdm

SIMILARITY_TRESHOLD: float = 0.7
NLP_ENABLED: bool = True
HEADLESS_POLICY: str | None = None


class LazyNlp:
    _nlp: Language | None = None
    _nlp_type: str

    def __init__(self, nlp_type: str) -> None:
        self._nlp_type = nlp_type

    def get_nlp(self):
        if self._nlp is None:
            self._nlp = spacy.load(self._nlp_type)
        return self._nlp

    @property
    def nlp(self):
        return self.get_nlp()

    def is_text_same(self, t1: str, t2: str):
        s1 = self.nlp(t1)
        s2 = self.nlp(t2)
        similarity = s1.similarity(s2)
        if similarity > SIMILARITY_TRESHOLD:
            print(similarity, 't1:', t1, 't2:', t2)
        return similarity > SIMILARITY_TRESHOLD




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
def merge_files(nlp: LazyNlp,filenames: list[str]) -> list[OrgNode]:
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


def run(filenames: list[str]):
    print('ready to go!')
    nlp = LazyNlp('en_core_web_md')
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

    global HEADLESS_POLICY, NLP_ENABLED, SIMILARITY_TRESHOLD
    HEADLESS_POLICY = args.headless_policy

    if args.disable_nlp:
        NLP_ENABLED = False
    SIMILARITY_TRESHOLD = args.similarity_treshold

    run(args.filenames)


if __name__ == '__main__':
    main()
