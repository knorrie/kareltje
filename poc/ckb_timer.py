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
import os
import pwd
import time
import yaml
from collections import namedtuple
from todoist_api_python.api import TodoistAPI


RGB = namedtuple('RGB', ['r', 'g', 'b'])
red = RGB(0xff, 0x00, 0x00)
orange = RGB(0xff, 0x7f, 0x00)
green = RGB(0x00, 0x7f, 0x00)

KeyboardKey = namedtuple('KeyboardKey', ['name', 'timespan', 'color'])

keys = [
    KeyboardKey('f1', 300, red),
    KeyboardKey('f2', 300, orange),
    KeyboardKey('f3', 300, orange),
    KeyboardKey('f4', 300, green),
    KeyboardKey('f5', 300, green),
    KeyboardKey('f6', 300, green),
    KeyboardKey('f7', 300, green),
    KeyboardKey('f8', 300, green),
    KeyboardKey('f9', 300, green),
    KeyboardKey('f10', 300, green),
    KeyboardKey('f11', 300, green),
    KeyboardKey('f12', 300, green),
    KeyboardKey('prtscn', 3600, green),
    KeyboardKey('scroll', 3600, green),
    KeyboardKey('pause', 3600, green),
]

ckb_cmd_pipe_path = '/dev/input/ckb1/cmd'
update_interval = 60
todoist_poll_interval = 900


def ckb_cmd(key, seconds):
    brightness_fraction = max(seconds / key.timespan, 0)
    output_color = RGB(*[round(_ * brightness_fraction) for _ in key.color])
    return("rgb {}:{:0>2x}{:0>2x}{:0>2x}".format(
        key.name, output_color.r, output_color.g, output_color.b))


def timer_commands(keys, remaining_seconds):
    for key in keys:
        if remaining_seconds >= key.timespan:
            yield ckb_cmd(key, key.timespan)
        else:
            yield ckb_cmd(key, max(remaining_seconds, 0))
        remaining_seconds = remaining_seconds - key.timespan


def ckb_cmd_write(target, lines):
    with open(target, 'w') as f:
        for line in lines:
            print(line, file=f)


def do_timer(end_time):
    while True:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        remaining_seconds = (end_time - now).total_seconds()
        ckb_cmd_write(ckb_cmd_pipe_path, timer_commands(keys, remaining_seconds))
        if now > end_time:
            break
        time.sleep(remaining_seconds % update_interval)


def get_next_timer_task(api):
    tasks = api.get_tasks(filter='@timer & due before: +4 hours')
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    for task in sorted(tasks, key=lambda _: _.due.datetime):
        # todoist uses RFC3339 UTC, e.g. '2022-11-28T12:00:00Z'
        # datetime can't do Z, so swap it with zero offset
        end_time = datetime.datetime.fromisoformat(task.due.datetime[:-1] + '+00:00')
        if end_time > now:
            return end_time, task
    return None, None


def do_todoist_timer(token):
    api = TodoistAPI(token)
    while True:
        end_time, task = get_next_timer_task(api)
        if task is not None:
            do_timer(end_time)
        else:
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            time.sleep(todoist_poll_interval - (now.timestamp() % todoist_poll_interval))


def load_config():
    homedir = pwd.getpwuid(os.getuid())[5]
    poc_config_file = os.path.join(homedir, '.config/kareltje/poc.yaml')
    with open(poc_config_file) as f:
        return yaml.safe_load(f.read())


def main():
    do_todoist_timer(load_config()['timer']['todoist']['token'])


if __name__ == '__main__':
    main()
