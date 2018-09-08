import gc
import objgraph

GLOBAL_ORC = 'Mogka'

def show_references():
    x = []
    y = [x, [x], dict(x=x)]
    objgraph.show_refs([y], filename='y-references.png')


def show_back_references():
    x = []
    y = [x, [x], dict(x=x)]
    objgraph.show_backrefs([x], filename='x-back-references.png')


class LeakedOne:
    pass

def func_that_will_leak(d={}):
    d['kochan'] = dict(mofo1=LeakedOne(),
                       mofo2=LeakedOne())
    wont_leak = LeakedOne()
    
def show_leaked():
    objgraph.show_growth()
    func_that_will_leak()
    print('--- This leaked')
    # this will show we have leaked references 
    objgraph.show_growth()


def show_chain_of_leaked():
    # LeakedOne must be leaked for this to work
    import random
    func_that_will_leak()
    objgraph.show_chain(
        objgraph.find_backref_chain(
            random.choice(objgraph.by_type('LeakedOne')),
            objgraph.is_proper_module),
        filename='chain-to-leaked.png')

def show_leaked_objects():
    """ not very useful """
    func_that_will_leak()
    gc.collect()
    roots = objgraph.get_leaking_objects()
    print('roots len = %s' % len(roots))
    objgraph.show_most_common_types(objects=roots)
    objgraph.show_refs(roots[:3], refcounts=True, filename='roots.png')
    
def show_refs_from_module():
    import sys
    current_module = sys.modules[__name__]
    print(current_module)
    func_that_will_leak()
    objgraph.show_refs([current_module], 
                       filename='references-from-main.png',
                       too_many=100,
                       refcounts=True)

def run():
    # show_references()
    # show_back_references()
    # show_leaked()
    # show_chain_of_leaked()
    # show_leaked_objects()
    show_refs_from_module()
    

if __name__ == '__main__':
    run()


"""
Install:
1. To draw the graphs download Graphviz from  
https://graphviz.gitlab.io/_pages/Download/Download_windows.html
Once installed add the bin folder to the Path variable
2. pip install objgraph
3. check the quickstart https://mg.pov.lt/objgraph/
"""
