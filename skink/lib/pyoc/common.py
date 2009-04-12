import os, fnmatch

def merge_dicts(priority_dict, other_dict):
    new_dict = {}
    
    for key, value in other_dict.items():
        new_dict[key] = value
    
    for key, value in priority_dict.items():
        new_dict[key] = value
        
    return new_dict

def locate(pattern, root=os.curdir, recursive=True):
    root_path = os.path.abspath(root)
    if recursive:
        for path, dirs, files in os.walk(root_path):
            for filename in fnmatch.filter(files, pattern):
                yield os.path.join(path, filename)
    else:
        for filename in fnmatch.filter(os.listdir(root_path), pattern):
            yield os.path.join(root_path, filename)

def camel_case(module_name):
        names = module_name.split("_")
        newName = []
        for name in names:
            newName.append(name[:1].upper() + name[1:])
        return "".join(newName)
