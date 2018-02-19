#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATADIR):
    os.makedirs(DATADIR)

for region, romfname, table_fname in (
        ('US', 'smrpgu.smc', 'tables_list.txt'),
        ('JP', 'smrpgj.smc', 'tables_list_jp.txt'),
):
    romfile = open(romfname, 'rb')

    for line in open(table_fname):
        line = line.strip()
        if line.startswith('#'):
            continue

        l = line.split()

        obj_size = 0
        for obj_line in open(l[1]):
            obj_line = obj_line.strip()
            if obj_line.startswith('#'):
                continue
            size = obj_line.split(',')[1]
            if size[:3] == 'bit':
                size = 1
            elif size == '?':
                size = 0
            obj_size += int(size)

        obj_name = l[0]
        addr = int(l[2], 16)
        num_objs = int(l[3])

        if len(l) > 4:
            obj_size = int(l[6]) if len(l) > 6 else 2

        romfile.seek(addr)
        data = romfile.read(obj_size * num_objs)

        dumpfile = os.path.join(DATADIR, region + "_" + obj_name + "_data.py")
        f = open(dumpfile, 'w')
        f.write("DATA = ")
        f.write(repr(data))
        f.write('\n')
        f.close()

    for suffix, start, end in (
            ('_pointer_data.py', 0x390000, 0x391C2A),
            ('_obj_seq_data.py', 0x259000, 0x280000),
            ('_obj_anim_data.py', 0x360000, 0x370000),
    ):
        fname = os.path.join(DATADIR, region + suffix)
        romfile.seek(start)
        f = open(fname, 'w')
        f.write("DATA = ")
        f.write(repr(romfile.read(end - start)))
        f.write("\n")
        f.close()

    romfile.close()
