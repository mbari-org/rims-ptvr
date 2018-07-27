from rois.model import Image, LabelInstance, Label, LabelSet


def run(*args):

    

    if len(args) < 2:
        print('need two argumnts: old_label new_label')
        return

    l_new = Label.objects.filter(name=args[1])
    
    if not l_new.exists():
        l_new = Label(
                name=args[1],
                description=args[1],
                full_name=args[1]
        )
    
    l_old = Label.objects.filter(name=args[0])

    if not l_old.exists():
        print('found no label to rename')
        return

    for im in Image.objects.filter(user_labels__name=l_old.name):
        im.user_labels.add(l_new)
        im.user_labels.remove(l_old)
        im.save()

    for im in Image.objects.filter(machine_labels__name=l_old.name):
        im.machine_labels.add(l_new)
        im.machine_labels.remove(l_old)
        im.save()

    for im in LabelInstance.objects.filter(label__name=l_old.name):
        im.label = l_name
        im.save()
