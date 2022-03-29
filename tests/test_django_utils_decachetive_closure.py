
invalidators = []


def _connect_invalidator(prefix):
    print("_connect_invalidator", prefix)

    for suffix in ['s1', 's2']:

        def invalidator():  # (suffix=suffix)
            print("invalidate", prefix, suffix)

        print('  connect %s %s, id:%s, __closure__:%s' % (prefix, suffix, id(invalidator), [(c, c.cell_contents) for c in invalidator.__closure__]))
        invalidators.append(invalidator)


_connect_invalidator('p1')
_connect_invalidator('p2')

for invalidator in invalidators:
    invalidator()
