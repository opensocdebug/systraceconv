# Copyright 2019 The Open SoC Debug Project
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import babeltrace
from babeltrace import CTFWriter

from .handlers import get_default_handlers, load_handlers, HandlerContainer
from .thread import ThreadState


class Converter(object):
    def __init__(self, json_files = []):
        self.threads = {}
        self.handlers = HandlerContainer()
        self.handlers.update(get_default_handlers())
        self.handlers.update(load_handlers(json_files))

    def convert(self, from_dir, to_dir):
        tc = babeltrace.TraceCollection()
        tc.add_trace(from_dir, "ctf")

        clock = CTFWriter.Clock("clk")
        writer = CTFWriter.Writer(to_dir)
        writer.add_clock(clock)
        stream_class = CTFWriter.StreamClass('trace')
        stream_class.clock = clock
        stream_class.packet_context_type.add_field(CTFWriter.IntegerFieldDeclaration(32), "cpu_id")

        for id, clslst in self.handlers.items():
            for cls in clslst:
                for ev in cls.get_generated_events():
                    stream_class.add_event_class(ev)

        stream = {}

        for e in tc.events:
            clock.time = e.timestamp
            id = e["cpu_id"]
            if id not in self.threads:
                self.threads[id] = ThreadState(self.handlers)
                stream[id] = writer.create_stream(stream_class)
                stream[id].packet_context.field("cpu_id").value = id
            evl = self.threads[id].consume(e)
            for ev in evl:
                stream[id].append_event(ev)

        for s in stream.values():
            s.flush()


def main():
    parser = argparse.ArgumentParser(description='Convert System Traces for Tracecompass')
    parser.add_argument('from_dir')
    parser.add_argument('to_dir')
    parser.add_argument('-j', action='append', default=[])
    args = parser.parse_args()

    conv = Converter(args.j)
    conv.convert(args.from_dir, args.to_dir)


if __name__ == "__main__":
    main()