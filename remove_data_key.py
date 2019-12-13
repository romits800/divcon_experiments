
def remove_data(d):
    if d.has_key('data'):
        del d['data']


def remove_all_data(d):
    remove_data(d)
    for k in d.keys():
        if type(k) == type(dict()):
            remove_all_data(k)
