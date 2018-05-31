# coding:utf-8
from os import listdir
from os.path import isfile, join, isdir
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

import re
import sys
import json
import argparse

reload(sys)
sys.setdefaultencoding('utf-8')


class TestHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.output = {}
        self.temp_output = []
        self.insideTable = False
        self.table_row_index = 0
        self.table_column_index = 0
        self.table_column_count = 0
        self.table = {}
        self.table_column_rowspan_datas = {}
        self.table_column_rowspan_indexes = {}
        self.table_column_rowspan = 0
        self.table_column_colspan = 0

    def handle_starttag(self, tag, attrs):
        # print "Start tag:", tag
        if tag == 'table':
            self.table = {}
            self.table_column_rowspan_datas = {}
            self.table_column_rowspan_indexes = {}
            self.table_row_index = 0
        if tag == 'tr':
            self.table_column_index = 0
        if tag == 'td':
            for attr in attrs:
                print attr[0] + " / " + attr[1]
                if attr[0] == 'rowspapn':
                    self.table_column_rowspan_indexes[self.table_column_index] = int(attr[1])
                    self.table_column_rowspan = int(attr[1])
                if attr[0] == 'colspan':
                    self.table_column_colspan = int(attr[1])
            self.insideTable = True
            if self.table_row_index == 0:
                print "column_index_init" + str(self.table_column_index)
                for i in range(max(1, self.table_column_colspan)):
                    self.table[self.table_column_index + i] = []

        # for attr in attrs:
            # print "     attr:", attr

    def handle_endtag(self, tag):
        if tag == 'table':
            self.temp_output.append(self.table)
            print self.table
            # cPickle.dump(self.table, open("test_table%d.pkl" % (len(self.temp_output)), "wb"))
        if tag == 'tr':
            if self.table_row_index == 0:
                self.table_column_count = self.table_column_index
            self.table_row_index += 1
        if tag == 'td':
            self.insideTable = False
            self.handle_extra_columns()
            if len(self.table[self.table_column_index]) != self.table_row_index + 1:
                self.append_table_data(' ')
            self.table_column_index += 1
        # print "End tag  :", tag

    def handle_data(self, data):
        # print "Data     :", re.sub('\s+', '', data)
        data = re.sub('\s+', '', data).decode('UTF-8')
        if not self.insideTable:
            if len(data) > 0:
                self.temp_output.append(data)
        else:
            if len(data) > 0:
                if self.table_column_colspan > 0:
                    for i in range(self.table_column_colspan):
                        self.append_table_data(data)
                    self.table_column_index = self.table_column_index + self.table_column_colspan - 1
                    self.table_column_colspan = 0
                else:
                    while (self.table_column_index in self.table_column_rowspan_indexes and
                           self.table_column_rowspan_indexes[self.table_column_index] > 0):
                        if self.table_column_index not in self.table_column_rowspan_datas:
                            self.table_column_rowspan_datas[self.table_column_index] = data
                        self.handle_extra_columns()
                        self.append_table_data(self.table_column_rowspan_datas[self.table_column_index])
                        self.table_column_rowspan_indexes[self.table_column_index] -= 1
                        self.table_column_index += 1
                    self.append_table_data(data)

    def append_table_data(self, data):
        self.handle_extra_columns()
        self.table[self.table_column_index].append(data)

    def handle_extra_columns(self):
        if self.table_column_index not in self.table:
            self.table[self.table_column_index] = []
            while len(self.table[self.table_column_index]) < self.table_row_index:
                self.table[self.table_column_index].append(' ')

    # def handle_comment(self, data):
        # print "Comment  :", data

    def handle_entityref(self, name):
        c = unichr(name2codepoint[name])
        # print "Named ent:", c

    def handle_charref(self, name):
        if name.startswith('x'):
            c = unichr(int(name[1:], 16))
        else:
            c = unichr(int(name))
        # print "Num ent  :", c

    # def handle_decl(self, data):
        # print "Decl     :", data

    def clear(self):
        self.output = {}
        self.temp_output = []
        self.insideTable = False
        self.table_row_index = 0
        self.table_column_index = 0
        self.table_column_count = 0
        self.table = {}
        self.table_column_rowspan_datas = {}
        self.table_column_rowspan_indexes = {}
        self.table_column_rowspan = 0
        self.table_column_colspan = 0


def check_args_validity(parsed_args):
    mode = parsed_args.mode
    if mode == 'single':
        if isdir(parsed_args.input_path) or isdir(parsed_args.output_path):
            return False
    else:
        if isfile(parsed_args.input_path) or isfile(parsed_args.output_path):
            return False
    return True


if __name__ == '__main__':

    argparser = argparse.ArgumentParser(description='Program to convert html data into json form. '
                                                    'This program works either in single mode or batch mode.'
                                                    'Please be informed that in single mode, both input_path/'
                                                    'output_path should be a file path.'
                                                    'In Batch mode, both input_path/output_path should be a dir path.')
    argparser.add_argument('input_path', help='path of input file/directory')
    argparser.add_argument('output_path', help='path of output file/directory')
    argparser.add_argument('--mode', nargs='?', choices=['single', 'batch'], default='single',
                           help='which mode should this program works in')
    args = argparser.parse_args()
    print args
    print check_args_validity(args)

    if not check_args_validity(args):
        argparser.print_help()
        exit()

    mode = args.mode
    input_path = args.input_path
    output_path = args.output_path

    if mode == 'single':
        with open(input_path, 'r') as html_content:
            content = html_content.read()
            parser = TestHTMLParser()
            parser.feed(content)
            json.dump(parser.temp_output, open(output_path, 'wb'), ensure_ascii=False,
                      indent=4)
            parser.clear()
    else:
        input_files = [f for f in listdir(input_path) if isfile(join(input_path, f))]
        for file_name in input_files:
            with open(join(input_path, file_name), 'r') as html_content:
                content = html_content.read()
                parser = TestHTMLParser()
                parser.feed(content)
                json.dump(parser.temp_output, open(join(output_path, file_name) + '.json', 'wb'),
                          ensure_ascii=False, indent=4)
                parser.clear()
