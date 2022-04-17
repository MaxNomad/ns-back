class SafeJson:
    def __init__(self, my_dict: dict):
        self.my_dict = my_dict
        self._safe_values = []
        self._safe_dict = {}

    def init_keys(self, *args):
        for item in args:
            if item and isinstance(item, list):
                if len(item) == 2:
                    key = item[0]
                    exp_type = item[1]
                    if isinstance(key, str) and isinstance(exp_type, type):
                        if key in self.my_dict:
                            value = self.my_dict[key]
                            got_type = type(value)
                            if value is not None:
                                if isinstance(value, exp_type):
                                    self._safe_values.append(value)
                                    self._safe_dict.update({key: value})
                                else:
                                    return {'message': f"Error: Value of key '{key}' must be type of '{exp_type}', got type '{got_type}'"}
                            else:
                                return {'message': f"Error: Value of key '{key}' must be type not None!"}
                        else:
                            return {'message': f"Error: There is no key '{key}' in json"}
                    else:
                        raise SyntaxError("SafeJson init_keys method input parameters must look like: [key, type]")
                else:
                    raise SyntaxError("SafeJson init_keys method input parameters must be list of 2 elements")
            else:
                raise SyntaxError("SafeJson init_keys method input parameters must be lists")

    def get_values(self):
        return self._safe_values

    def get_verified_dict(self):
        return self._safe_dict

    def __getitem__(self, key):
        return self.my_dict[key]

    def __setitem__(self, key, value):
        self.my_dict[key] = value

    def __repr__(self):
        return repr(self.my_dict)

    def __len__(self):
        return len(self.my_dict)

    def __delitem__(self, key):
        del self.my_dict[key]

    def clear(self):
        return self.my_dict.clear()

    def copy(self):
        return self.my_dict.copy()

    def has_key(self, k):
        return k in self.my_dict

    def update(self, *args, **kwargs):
        return self.my_dict.update(*args, **kwargs)

    def keys(self):
        return self.my_dict.keys()

    def values(self):
        return self.my_dict.values()

    def items(self):
        return self.my_dict.items()

    def pop(self, *args):
        return self.my_dict.pop(*args)

    def __contains__(self, item):
        return item in self.my_dict

    def __iter__(self):
        return iter(self.my_dict)

