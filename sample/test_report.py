#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :


class Test:
    """TEST CODE"""

    def __init__(self):
        pass
        return

    def report(self, foo):  # To Be Overriden
        print(foo)
        return

    def main(self):
        self.report("HELLO")
        return


T = Test()

print("=====")
T.main()
print("=====")
T.report("OOPS")
print("=====")

# This allows different reporting style for TUI/CLI
