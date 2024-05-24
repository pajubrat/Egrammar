def determine_language(features):
    return [f for f in features if f.startswith('LANG:')]

def fformat(f):
    if f.startswith('+COMP') or f.startswith('+SPEC'):
        return f.split(':')[0], set(f.split(':')[1].split(','))
    return None, None

def sWMcopy(sWM, SO):
    def get_mirror(x, M):
        return next((m[1] for m in M if x == m[0]), None)

    M = [(x, x.copy()) for x in sWM]
    # Mirror horizontal adjunct dependencies
    for m in M:
        if m[0].adjunct():
            m[1].mother_ = get_mirror(m[0].mother(), M)
    SO_ = [get_mirror(x, M) for x in SO]  # Selected objects in the new sWM
    sWM_ = [x[1] for x in M if x[1] not in SO_]
    return set(sWM_), tuple(SO_)

def print_lst(lst):
    str = ''
    for i, ps in enumerate(lst):
        if ps.terminal():
            if ps.sublexical():
                str += f'{ps}'
            else:
                str += f'{ps}°'
        else:
            str += f'{ps}'
        if i < len(lst) - 1:
            str += ', '
    return str

def print_sWM(sWM):
    aWM = [f'{x}' for x in sWM if not x.adjunct()]
    iWM = [f'{x.mother().head().lexical_category()}P|{x}' for x in sWM if x.adjunct()]
    s = f'{", ".join(aWM)}'
    if iWM:
        s += f'{{ {", ".join(iWM)} }}'
    return s

def print_dictionary(sem):
    str = ''
    for key in sem.keys():
        if sem[key]:
            str += key + ': '
            for value in sem[key]:
                if value:
                    str += f'{value}, '
    return str[:-2]

def get_root(sWM):
    return next((x for x in sWM if x.isRoot()), None)

def tcopy(SO):
    return {x.copy() for x in SO}

def tset(X):
    if isinstance(X, set):
        return X
    else:
        return {X}

def comment(line):
    return line.startswith('#')

def well_formed_lexical_entry(line):
    return '::' in line
