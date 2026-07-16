from contextlib import contextmanager


class Tracer:
    @contextmanager
    def span(self, name: str, **attributes):
        yield
