#!/usr/bin/python3
#
# Copyright (C) 2022 Hans van Kranenburg <hans@knorrie.org>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import datetime
import json
import time

update_interval = 5


def main():
    print("""{"version":1}""")
    print("[")
    while True:
        now = datetime.datetime.now()
        line = [
            {
                "color": "#00FF00",
                "full_text": "It's not easy being green.",
            },
            {
                "full_text": now.strftime("%a %Y-%m-%d %H:%M:%S"),
            },
        ]
        print(json.dumps(line), flush=True)
        time.sleep(update_interval - (now.timestamp() % update_interval))
        print(",", end='')


if __name__ == '__main__':
    main()
