

class Enum(object):
    @classmethod
    def __iter__(cls):
        iterator = [(attr, value) for attr, value in cls.__dict__.items() if str(attr).isupper()]
        for attr, value in iterator:
            yield str(attr), str(value)

    def keys(self):
        return [k for k, v in self]

    def values(self, exclude=None):
        exclude = [] if exclude is None else exclude
        exclude = [exclude] if not isinstance(exclude, list) else exclude
        return [v for k, v in self if v not in exclude]
