from bioservices import KEGG

def search_organism(organism):
    k = KEGG()
    return k.lookfor_organism(organism)