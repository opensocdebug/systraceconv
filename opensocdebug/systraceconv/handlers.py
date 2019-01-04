# Copyright 2019 The Open SoC Debug Project
#
# SPDX-License-Identifier: Apache-2.0

import json
from babeltrace import CTFWriter


class Handler(object):
    pass


class HandlerContainer(dict):
    def __getitem__(self, item):
        if self.get(item) is None:
            self.__setitem__(item, [])

        return self.get(item)

    def update(self, E):
        for id in E.keys():
            lst = self.__getitem__(id)
            if isinstance(E[id], list):
                lst += E[id]
            else:
                lst.append(E[id])

    def instantiate(self):
        inst = {}
        for id, funcs in self.items():
            inst[id] = []
            for f in funcs:
                inst[id] = [f()]
        return inst


event_printf = CTFWriter.EventClass("printf")
event_printf.add_field(CTFWriter.StringFieldDeclaration(), "str")


class StdoutHandler(Handler):
    def __init__(self):
        self.str = ""

    @staticmethod
    def get_generated_events():
        return [event_printf]

    def consume(self, event):
        ev = None
        value = event["value"]
        if value not in (10, 13):
            self.str += chr(value)
        if value == 10:
            self.str += chr(0)
            ev = CTFWriter.Event(event_printf)
            ev.payload("str").value = self.str
            self.str = ""
        return ev


def generate_composite_event(name, fields, static_fields):
    ev = CTFWriter.EventClass(name)
    for f in static_fields.keys():
        ev.add_field(CTFWriter.StringFieldDeclaration(), f)
    for f in fields:
        ev.add_field(CTFWriter.IntegerFieldDeclaration(32), f)
    return ev


def generate_composite_handler(name, fields, static_fields):
    class CompositeHandler(Handler):
        event = generate_composite_event(name, fields, static_fields)

        def __init__(self):
            self.name = name
            self.fields = fields
            self.values = []
            self.static_fields = static_fields

        @staticmethod
        def get_generated_events():
            return [CompositeHandler.event]

        def consume(self, event):
            ev = None
            self.values.append(event["value"])
            if len(self.values) == len(self.fields):
                ev = CTFWriter.Event(CompositeHandler.event)
                for name, value in self.static_fields.items():
                    ev.payload(name).value = value

                for name, value in dict(zip(self.fields, self.values)).items():
                    ev.payload(name).value = value

            return ev

    return CompositeHandler


def get_default_handlers():
    handlers = {
        4: [StdoutHandler],
        15: [generate_composite_handler("reset", ["dummy"], {})],
        16: [generate_composite_handler("exception_enter", ["type"], { "fname": "exception" })],
        17: [generate_composite_handler("exception_leave", ["dummy"], { "fname": "exception" })]
    }
    return handlers


def load_handlers(json_files):
    if not isinstance(json_files, list):
        json_files = [json_files]

    handlers = HandlerContainer()

    for f in json_files:
        with open(f) as fp:
            events = json.load(fp)

            for ev in events:
                id = int(ev["id"], 0)
                name = ev["name"]
                fields = ev["fields"]
                static_fields = ev.get("static_fields", {})

                handlers[id].append(generate_composite_handler(name, fields, static_fields))

    return handlers
