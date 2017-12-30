class Match:
    """
    with Match(expr) as match:
        for (a, b) in match.case(pattern1):
            do_something()
        for (a, b, c) in match.case(pattern2):
            do_something()
        else:
            print('matched nothing')
    """
    def __init__(self, expr):
        self.expr = expr
        self.captured = None

    def __enter__(self, expr):
        self.expr = expr

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def case(self, pattern):
        # TODO : generate `captured` from `expr` and `pattern`
        pass

    def __iter__(self):
        if self.expr is None:
            return None
        yield self.captured



