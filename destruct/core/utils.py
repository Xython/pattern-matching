from typing import Optional


def constant_true(*_, **__):
    return True


class Node:
    def __init__(self, content=None):
        self.next = None
        self.content = content

    def __str__(self):
        return self.content.__str__()

    def __repr__(self):
        return self.content.__str__()


class LinkedList:
    def __init__(self, head_end=None):
        if head_end:
            self.head, self.end = head_end
        else:
            self.head: Optional[Node] = None
            self.end: Optional[Node] = None

    def append_node(self, node):
        try:
            self.end.next = node
        except AttributeError:
            self.head = self.end = node
        self.end = node

    def __getitem__(self, item):
        node = self.head
        for i in range(item):
            if not node.next:
                return None
            node = node.next
        return node

    def append(self, v):
        self.append_node(Node(v))

    def append_left_node(self, node):
        node.next = self.head
        self.head = node
        if self.end is None:
            self.end = node

    def append_left(self, v):
        self.append_left_node(Node(v))

    def extend(self, linked_list):
        self.end.next = linked_list.head
        self.end = linked_list.end

    def extend_left(self, linked_list):
        linked_list.end.next = self.head
        self.head = linked_list.head

    def __iter__(self):
        if self.head is None:
            return None
        else:
            n = self.head
            while n.next:
                yield n.content
                n = n.next
            yield n.content

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return [n for n in self].__str__()

    @property
    def tail(self):
        return LinkedList(head_end=(self.head.next, self.end) if self.head is not self.end else None)

    @property
    def to_list(self):
        return list(self)

    @property
    def to_tuple(self):
        return tuple(self)

    @property
    def copy(self):
        return LinkedList.from_iter(self)

    @staticmethod
    def from_iter(sequence):
        _list = LinkedList()
        for elem in sequence:
            _list.append_node(Node(elem))
        return _list
