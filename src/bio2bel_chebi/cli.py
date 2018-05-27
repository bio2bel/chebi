# -*- coding: utf-8 -*-

"""The CLI for Bio2BEL ChEBI."""

from .manager import Manager

main = Manager.get_cli()

if __name__ == '__main__':
    main()
