#!/usr/bin/env python3

import orgparse as org

# TODO add console argument parsing
# import argparse


# display node
def print_content(node):
    print(node)
    for child in node[1:]:
        print_content(child)


# merge nodes or not
def are_nodes_same(n1: org.OrgNode, n2: org.OrgNode) -> bool:
    if n1.heading == n2.heading and n1.body == n2.body:
        return True
    return False


def is_inbox(n: org.OrgNode):
    # TODO generalize stuff
    return n.todo == 'INBOX'


# # return is merge success
# def merge_same_nodes(n1: org.OrgNode, n2: org.OrgNode):
#     if is_inbox(n1):
#         slave = n1
#         master = n2
#     elif is_inbox(n2):
#         slave = n1
#         master = n2
#     else:
#         return False
#     print(slave)
#     print(master)


# compare two files
def find_dups(filename1, filename2) -> tuple[list[str], list[str]]:
    f1 = org.load(filename1)
    f2 = org.load(filename2)
    f1_dups = []
    f2_dups = []

    for n1 in f1[1:]:
        for n2 in f2[1:]:
            if not are_nodes_same(n1, n2):
                continue
            if is_inbox(n1):
                f1_dups.append(str(n1))
            elif is_inbox(n2):
                f2_dups.append(str(n2))
            elif (
                n1.todo == n2.todo
                and n1.scheduled == n2.scheduled
                and n1.clock == n2.clock
                and n1.deadline == n2.deadline
            ):
                f1_dups.append(str(n2))

    return (f1_dups, f2_dups)


# delete dups from file
def delete_dups(src: str, dst: str, dups: list[str]):
    with open(src, 'r') as f:
        content = f.read()

    source_content = content
    # print(content)
    # print('-' * 5)
    for d in dups:
        # print(d)
        content = content.replace(d, '')
    # print('-' * 5)
    # print(content)
    print(source_content == content)
    if source_content != content:
        with open(dst, 'w') as f:
            f.write(content)


def run(filename1, filename2):
    dup1, dup2 = find_dups(filename1, filename2)
    delete_dups(filename1, 'out-' + filename1, dup1)
    # print('=' * 5)
    delete_dups(filename2, 'out-' + filename2, dup2)


def main():

    run('test1.org', 'test2.org')


if __name__ == '__main__':
    main()
