def is_unittest(argv):
    if any(pattern in arg for pattern in ['uwsgi'] for arg in argv):
        return False
    elif any(pattern in arg for pattern in ['unittest'] for arg in argv):
        return True

    return False
