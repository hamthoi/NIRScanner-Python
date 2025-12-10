#!/usr/bin/env python3
"""Check Python version and ABI info useful for building native extension.

Run on the Pi before attempting to use the prebuilt binary to verify compatibility.
"""
import sys
import sysconfig

def main():
    print('sys.version:', sys.version)
    print('sys.version_info:', tuple(sys.version_info))
    print('platform:', sys.platform)
    print('executable:', sys.executable)
    print('python_build:', sysconfig.get_config_var('Py_DEBUG'))
    print('EXT_SUFFIX:', sysconfig.get_config_var('EXT_SUFFIX'))
    print('SOABI:', sysconfig.get_config_var('SOABI'))
    print('INCLUDEPY:', sysconfig.get_paths().get('include'))

if __name__ == '__main__':
    main()
