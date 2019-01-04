# Copyright 2019 The Open SoC Debug Project
#
# SPDX-License-Identifier: Apache-2.0

class ThreadState(object):
    def __init__(self, handlers):
        self.handlers = handlers.instantiate()

    def consume(self, event):
        id = event["id"]

        if id not in self.handlers:
            print("Unhandled event id: 0x{:04x}".format(id))
            return []

        evl = []

        for h in self.handlers[id]:
            ev = h.consume(event)
            if ev is not None:
                evl.append(ev)

        return evl
