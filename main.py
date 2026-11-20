#!/usr/bin/env python3
"""Universal launcher for BrodGSI (GUI and CLI)."""

import sys


def main():
    if len(sys.argv) <= 1:
        # No arguments -> launch GUI
        from brodgsi_gui import main as gui_main

        return gui_main()

    cmd = sys.argv[1].lower()

    if cmd in ("gui", "--gui", "-g"):
        from brodgsi_gui import main as gui_main

        # Forward any remaining arguments
        sys.argv.pop(1)
        return gui_main()

    if cmd in ("cli", "--cli"):
        import cli

        sys.argv.pop(1)
        return cli.main()

    # If first argument is standard CLI command or flag
    if cmd in ("build", "rebuild", "list", "clean", "-h", "--help"):
        import cli

        return cli.main()

    # Fallback to CLI parser
    import cli

    return cli.main()


if __name__ == "__main__":
    sys.exit(main())
