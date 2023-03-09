#!/usr/bin/env python3

import argparse
import orgparse as org
import spacy
import random
from orgparse.node import OrgNode
from tqdm import tqdm

SIMILARITY_TRASHOLD = 0.7
nlp = spacy.load('en_core_web_md')


# display node
def print_content(node: OrgNode):
    # print(node.heading)
    # print(node.body)
    print(str(node), f'tags: {node.tags}')
    # for child in node[1:]:
    #     print_content(child)


def is_text_same(t1: str, t2: str):
    s1 = nlp(t1)
    s2 = nlp(t2)
    similarity = s1.similarity(s2)
    if similarity > SIMILARITY_TRASHOLD:
        print(similarity, 't1:', t1, 't2:', t2)

    return similarity > SIMILARITY_TRASHOLD


# check are nodes same or not
def are_nodes_same(n1: OrgNode, n2: OrgNode) -> bool:
    # speed up by direct comparing
    if n1.heading == n2.heading and n1.body == n2.body:
        return True

    return is_text_same(n1.heading, n2.heading) and is_text_same(
        n1.body, n2.body
    )


def resolve_same_nodes_conflict(n1: OrgNode, n2: OrgNode) -> list[OrgNode]:
    print('<<<<<', str(n1), '=====', str(n2), '>>>>>', sep='\n')
    print(
        'These entries seems to be very close. What whould you do?',
        '1) choose first entry',
        '2) choose second entry',
        '3) add unique tag to both (manual processing)',
        '4) create new task with both entiries in description (manual processing)',
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
        # FIXME tags are not added
        n1.tags.add(tag)
        n2.tags.add(tag)
        return [n1, n2]
    return []


# get list of filenames and return merged list of org entries
def merge_files(filenames: list[str]) -> list[OrgNode]:
    org_entries: list[OrgNode] = []
    for filename in filenames:
        f = org.load(filename)
        org_entries += f[1:]
    org_entries = list(
        filter(lambda x: x.heading != '' or x.body != '', org_entries)
    )

    # FIXME this is very inefficient and produce to many dups. As temporal fix
    # set is used, but it breaks tasks with subtasks!
    merged_entries: set[OrgNode] = set()
    for in1 in tqdm(range(len(org_entries)), desc="Merge progress"):
        for in2 in range(in1 + 1, len(org_entries)):
            n1 = org_entries[in1]
            n2 = org_entries[in2]
            if are_nodes_same(n1, n2):
                for resolve in resolve_same_nodes_conflict(n1, n2):
                    merged_entries.add(resolve)
                continue
            merged_entries.add(n1)
            merged_entries.add(n2)

    return list(merged_entries)


def run(filenames: list[str]):
    print('ready to go!')
    nodes = merge_files(filenames)
    for n in nodes:
        print_content(n)


def main():
    parser = argparse.ArgumentParser(
        description='Merge Orgmode files. Delete similar entries.'
    )
    parser.add_argument(
        'filenames', nargs='+', help='input orgmode files to merge'
    )
    args = parser.parse_args()
    run(args.filenames)


if __name__ == '__main__':
    main()
