from bioservices import KEGG

def search_organism(organism):
    k = KEGG()
    return k.lookfor_organism(organism)

def search_pathway(gene, organism):
    k = KEGG()
    return k.get_pathway_by_gene(gene, organism)