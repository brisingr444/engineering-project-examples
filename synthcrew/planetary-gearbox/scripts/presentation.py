"""Set installed instances visible and construction history hidden before GUI restoration."""
def visible_assembly(d):
    for o in d.Objects:
        if 'Visibility' in o.PropertiesList:o.Visibility=False
    for b in d.PartLibrary.Group:b.Tip.Visibility=True
    d.Gearbox.Visibility=True
    for g in d.Gearbox.Group:
        g.Visibility=True
        for o in g.Group:o.Visibility=True

