from bioservices import KEGG, QuickGO


def search_organism(organism):
    k = KEGG()
    return k.lookfor_organism(organism)


def search_pathway(gene, organism):
    k = KEGG()
    return k.get_pathway_by_gene(gene, organism)


# This is the only method currently called through dash.  It provided the user with a list of genes in a requested
# pathway.  If no pathway is found, it returns an error
def get_pathway(pathway):
    s = KEGG()
    data = s.get(pathway)
    if type(data) == int:
        return data
    dict_data = s.parse(data)
    path_info = (dict_data['NAME'], dict_data['GENE'])
    return path_info

def get_go(goid):
    s = QuickGO()
    res = s.Terms('GO:' + goid)
    return res
