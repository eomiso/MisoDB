def get_index(iterable, target, reverse = False, count = 1):
    """ Utility function for getting the index of the given entry in an iterable.
        target : the target entry to find in the iterable.
        reverse = True : count from the last, but return the normal index .
        count : number of occurences before returning the index.
    """
    n = 0
    cnt = 0

    if reverse:
        iterable = iterable[::-1]

    for c in iterable:
        if c == target:
            cnt += 1
            if count == cnt:
                return len(iterable) - (n+1) if reverse else n
        n += 1

    return -1

