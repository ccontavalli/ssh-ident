def enum(*sequential, **named):
    items = {}
    kwargs = {}
    for k, v in named.iteritems():
        if k[0].isupper():
            items[k] = v
        else:
            kwargs[k] = v

    seq = bool(kwargs.get('sequential'))
    if seq:
        enums = dict(zip(sequential, range(1, len(sequential) + 1)), **items)
    else:
        enums = dict(zip(sequential, map(lambda x: 2 ** (x - 1) if x > 0 else 0, range(len(sequential)))), **items)

    reverse = dict((value, key) for key, value in enums.iteritems())

    def not_implemented():
        raise NotImplementedError()

    def normalise(self, k):
        k = k.upper() if isinstance(k, basestring) else k
        return k if k in self and k in enums.values() else enums[k]

    def key_str(self, key_val):
        for k, v in enums.items():
            if v == key_val:
                return k
        return None
    meta = type('EnumMeta', (type,), {
        "__contains__": lambda self, v: v in enums.keys() or v in enums.values(),
        "__len__": lambda self: len(sequential),
        "__getitem__": lambda self, k: normalise(self, k),
        "__setattr__": lambda self, k, v: not_implemented(),
        "__setitem__": lambda self, k, v: not_implemented(),
        "__iter__": lambda self: iter(reverse.items()),
        "items": lambda self: reverse.items(),
        "kstr": lambda self, k: key_str(self, k),
    })

    d = {}
    d.update(enums)

    return meta('Enum', (object,), d)
