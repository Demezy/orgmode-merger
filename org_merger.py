import random

import orgparse as org
from orgparse.node import OrgNode
from tqdm import tqdm

from nlp import LazyNlp


class OrgMerger:
    _nlp_enabled: bool
    _headless_policy: str | None
    _nlp: LazyNlp

    def __init__(
        self,
        nlp: LazyNlp,
        nlp_enabled: bool = True,
        treshold: float = 0.7,
        headless_policy: str | None = None,
    ) -> None:
        self._nlp_enabled = nlp_enabled
        self._headless_policy = headless_policy
        self._treshold = treshold
        self._nlp = nlp

    # display node
    def print_content(self, node: OrgNode):
        print(str(node), f'tags: {node.tags}')

    # check are nodes same or not
    def are_nodes_same(self, n1: OrgNode, n2: OrgNode) -> bool:
        # speed up by direct comparing
        if n1.heading == n2.heading and n1.body == n2.body:
            return True

        return (
            self._nlp_enabled
            and self._nlp.is_text_same(n1.heading, n2.heading)
            and self._nlp.is_text_same(n1.body, n2.body)
        )

    def resolve_same_nodes_conflict(
        self, n1: OrgNode, n2: OrgNode
    ) -> list[OrgNode]:
        if self._headless_policy:
            choice = self._headless_policy
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
    def merge_files(self, filenames: list[str]) -> list[OrgNode]:
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
                if self.are_nodes_same(n1, n2):
                    for resolve in self.resolve_same_nodes_conflict(n1, n2):
                        merged_entries.add(resolve)
                    continue
                merged_entries.add(n1)
                merged_entries.add(n2)

        return list(merged_entries)

    def run(self, filenames: list[str]):
        nodes = self.merge_files(filenames)
        for n in nodes:
            self.print_content(n)
