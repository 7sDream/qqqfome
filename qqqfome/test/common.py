import warnings


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        test_func(self, *args, **kwargs)
    return do_test
