# coding:utf-8
from os import listdir
from os.path import isfile, join
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import re
import cPickle


class TestHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.output = []
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
            self.output.append(self.table)
            print self.table
            cPickle.dump(self.table, open("test_table%d.pkl" % (len(self.output)), "wb"))
        if tag == 'tr':
            if self.table_row_index == 0:
                self.table_column_count = self.table_column_index
            self.table_row_index += 1
        if tag == 'td':
            self.insideTable = False
            if len(self.table[self.table_column_index]) != self.table_row_index + 1:
                self.append_table_data(' ')
            self.table_column_index += 1
        # print "End tag  :", tag

    def handle_data(self, data):
        # print "Data     :", re.sub('\s+', '', data)
        data = data.strip().decode('UTF-8')
        if not self.insideTable:
            if len(data) > 0:
                self.output.append(data)
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
        self.output = []
        self.insideTable = False
        self.table_row_index = 0
        self.table_column_index = 0
        self.table_column_count = 0
        self.table = {}
        self.table_column_rowspan_datas = {}
        self.table_column_rowspan_indexes = {}
        self.table_column_rowspan = 0
        self.table_column_colspan = 0

dataset_dir_path = "C:\Users\ProgrammerYuan\Downloads\FDDC_announcements_round1_test_a_20180524" \
                   "\FDDC_announcements_round1_test_a_20180524\holdmore\html"
print(dataset_dir_path)
files = [f for f in listdir(dataset_dir_path) if isfile(join(dataset_dir_path, f))]

for file_name in files:
    with open(join(dataset_dir_path, file_name), 'r') as html_content:
        print file_name
        content = html_content.read()
        parser = TestHTMLParser()
        parser.feed(content)
        cPickle.dump(parser.output, open(join('output/', file_name), 'wb'))
        parser.clear()
