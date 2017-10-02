#!/usr/bin/env python

from sqlalchemy import create_engine

eng = create_engine("sqlite:///test.db")
conn = eng.connect()

conn.execute("create table x (a integer, b integer)")
conn.execute("insert into x (a, b) values (1, 1)")
conn.execute("insert into x (a, b) values (2, 2)")

result = conn.execute("select x.a, x.b from x")
assert result.keys() == ["a", "b"]

reader:
insert into images (channels, native data for node_id)
image
insert into nodes (node_id, platform, code, params, etc)

experiments:
request filename data and map to experiments table
insert into images (experiment_id)
insert into experiments (row, column, drugs/doses[], cell_type, URL to proceedure steps, microscope_info_placeholder)

filter:
insert into nodes (node_id, platform, code, params, etc)
insert into images (new filtered channel)

segmentation:
insert into nodes (node_id, platform, code, params, etc)
insert into images (new labelled channel, some label details)

tracking:
insert into images (some label details: tracking id per label)

visualization:
insert into nodes (node_id, platform, code, params, etc)
insert into images (movie id)
insert into movies (image ids)

