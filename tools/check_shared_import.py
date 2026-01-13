import sys
print('\n'.join(sys.path))
try:
    import shared.config
    print('FOUND', shared.config.__file__)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('IMPORT_ERR', e)
