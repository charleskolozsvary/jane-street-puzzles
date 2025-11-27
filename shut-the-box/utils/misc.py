def sumTuples(t1: tuple[int], t2: tuple[int]) -> tuple[int]:
    assert len(t1) == len(t2), 'lengths of supplied tuples do not match'
    return tuple(sum(z) for z in zip(t1, t2))
