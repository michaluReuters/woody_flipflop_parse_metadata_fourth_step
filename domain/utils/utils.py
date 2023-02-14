def convert_dict(d):
    """
    Converts dot-separated values in the given dictionary to nested values in a new dictionary.

    Args:
        d (dict): The dictionary to be converted.

    Returns:
        dict: A new dictionary with dot-separated values converted to nested values.
    """
    result = {}
    for key, value in d.items():
        if '.' in key:
            sub_keys = key.split('.')
            sub_dict = result
            for subkey in sub_keys[:-1]:
                if subkey not in sub_dict:
                    sub_dict[subkey] = {}
                sub_dict = sub_dict[subkey]
            sub_dict[sub_keys[-1]] = value
        else:
            result[key] = value
    return result
