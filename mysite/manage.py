#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import msvcrt

import sys
from multiprocessing import Process, Pipe




def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

# def f(conn):
#     conn.send([42, None, 'hello'])
#     conn.close()


if __name__ == '__main__':
    #parent_conn, child_conn = Pipe()
    #p = Process(target=f, args=(child_conn,))
    #p.start()
    #print(parent_conn.recv())   # prints "[42, None, 'hello']"
    # p.join()
    #자식 프로세스면 wait
    #부모면 main()
    main()
