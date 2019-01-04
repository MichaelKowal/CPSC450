from bioservices import KEGG, QuickGO


# This is the only method currently called through dash.  It provided the user with a list of genes in a requested
# pathway.  If no pathway is found, it returns an error
def get_pathway(pathway):
    s = KEGG()
    data = s.get(pathway)
    # KEGG returns many different ints as errors.  If this happens, simply return the error code and inform the user
    # that what they entered didn't work.
    if type(data) == int:
        return data
    dict_data = s.parse(data)
    # Right now we are only taking the name and the genes from the call. There is a lot of data getting excluded.
    path_info = (dict_data['NAME'], dict_data['GENE'])
    return path_info


# This is not currently being used but is left in in case someone wants to add in the GO later.
def get_go(goid):
    s = QuickGO()
    res = s.Terms('GO:' + goid)
    return res
