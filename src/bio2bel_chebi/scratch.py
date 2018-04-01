from bio2bel_chebi import Manager as ChebiManager

if __name__ == '__main__':
    m = ChebiManager()
    m._populate_relations()