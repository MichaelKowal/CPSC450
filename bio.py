from bioservices import KEGG


def search_organism(organism):
    k = KEGG()
    return k.lookfor_organism(organism)


def search_pathway(gene, organism):
    k = KEGG()
    return k.get_pathway_by_gene(gene, organism)


def get_pathway(pathway):
    s = KEGG()
    data = s.get(pathway)
    dict_data = s.parse(data)
    return dict_data['GENE']