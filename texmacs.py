import lldb
import lldb.formatters.Logger
import re
import os
from functools import partial


"""
Convinent for debug
command script import texmacs.py
"""

class texmacs_array_SyntheticChildrenProvider:
    def __init__(self, valobj, internal_dict):
        logger = lldb.formatters.Logger.Logger()
        self.valobj = valobj
        self.internal_dict = internal_dict
    def num_children(self):
        logger = lldb.formatters.Logger.Logger()
        data_len = self.valobj.GetValueForExpressionPath('.rep.n')
        return data_len.GetValueAsUnsigned(0)
    def get_child_at_index(self, index):
        logger = lldb.formatters.Logger.Logger()
        logger >> "Retrieving child " + str(index)
        if index < 0:
            return None
        if index >= self.num_children():
            return None
        try:
            return self.valobj.GetValueForExpressionPath('.rep.a' + '[' + str(index) + ']')
        except:
            return None

def texmacs_array_SummaryProvider(valobj, internal_dict, options):
    data_len = valobj.GetNonSyntheticValue().GetChildMemberWithName('n').signed
    return f'size={data_len}'

class texmacs_list_SyntheticChildrenProvider:
    def __init__(self, valobj, internal_dict):
        self.valobj = valobj
        self.internal_dict = internal_dict
    def num_children(self):
        count = 0
        rep = self.valobj.GetChildMemberWithName('rep')
        while rep.unsigned != 0:
            count += 1
            next_node = rep.GetChildMemberWithName('next')
            rep = next_node.GetChildMemberWithName('rep')
        return count

    def get_child_at_index(self, index):
        logger = lldb.formatters.Logger.Logger()
        logger >> "Retrieving child " + str(index)
        count = 0
        if index < 0:
            return None
        if index >= self.num_children():
            return None
        try:
            rep = self.valobj.GetChildMemberWithName('rep')
            if index == 0:
                return rep.GetChildMemberWithName('item')
            while count < index:
                next_node = rep.GetChildMemberWithName('next')
                rep = next_node.GetChildMemberWithName('rep')
                count += 1
            return rep.GetChildMemberWithName('item')
        except:
            return None

def texmacs_path_SummaryProvider(valobj, internal_dict):
    val_list = []
    rep = valobj.GetNonSyntheticValue().GetChildMemberWithName('rep')
    while rep.unsigned != 0:
        val = rep.GetChildMemberWithName('item').signed
        val_list.append(str(val))
        next_node = rep.GetChildMemberWithName('next')
        rep = next_node.GetChildMemberWithName('rep')
    return f'size={len(val_list)} [' + ', '.join(val_list) + ']'


def texmacs_rectangle_SummaryProvider(valobj, internal_dict):
    rep = valobj.GetChildMemberWithName('rep')
    x1 = rep.GetChildMemberWithName('x1').signed
    y1 = rep.GetChildMemberWithName('y1').signed
    x2 = rep.GetChildMemberWithName('x2').signed
    y2 = rep.GetChildMemberWithName('y2').signed

    return f"({x1}, {y1}) ({x2}, {y2})"


def texmacs_xkerning_SummaryProvider(valobj, internal_dict, options):
    padding = valobj.GetValueForExpressionPath('.rep.padding').signed
    left = valobj.GetValueForExpressionPath('.rep.left').signed
    right = valobj.GetValueForExpressionPath('.rep.right').signed
    return f'padding={padding}, left={left}, right={right}'

def texmacs_pencil_SummaryProvider(valobj, internal_dict, options):
    c = valobj.GetValueForExpressionPath('.rep.c').unsigned
    w = valobj.GetValueForExpressionPath('.rep.w').signed
    return f'c={c}, w={w}'

def texmacs_qt_proxy_renderer_rep_SummaryProvider(valobj, internal_dict, options):
    w = valobj.GetValueForExpressionPath('.w').signed
    h = valobj.GetValueForExpressionPath('.h').signed
    return f'w={w}, h={h}'

def texmacs_box_rep_SummaryProvider(valobj, internal_dict, options):
    rep = valobj
    x1 = rep.GetChildMemberWithName('x1').signed
    y1 = rep.GetChildMemberWithName('y1').signed
    x2 = rep.GetChildMemberWithName('x2').signed
    y2 = rep.GetChildMemberWithName('y2').signed

    return f"({x1}, {y1}) ({x2}, {y2})"

def texmacs_no_brush_rep_SummaryProvider(valobj, internal_dict, options):
    return "no_brush_rep"

def texmacs_brush_SummaryProvider(valobj, internal_dict, options):
    return valobj.GetChildMemberWithName('rep')

def texmacs_basic_character_SummaryProvider(valobj, internal_dict, options):
    unicode_val = valobj.GetChildMemberWithName('rep').GetChildMemberWithName('c').signed
    return chr(unicode_val)

def texmacs_font_SummaryProvider(valobj, internal_dict, options):
    return valobj.GetValueForExpressionPath('.rep.res_name')

def texmacs_coord2_SummaryProvider(valobj, internal_dict, options):
    x1 = valobj.GetValueForExpressionPath('.x1').signed
    x2 = valobj.GetValueForExpressionPath('.x2').signed
    return f'{x1},{x2}'

def texmacs_hashmap_SummaryProvider(valobj, internal_dict, options):
    size = valobj.GetValueForExpressionPath('.rep.size').signed
    n = valobj.GetValueForExpressionPath('.rep.n').signed
    max_val = valobj.GetValueForExpressionPath('.rep.max').signed
    return f'size={size},n={n},max={max_val}'

def texmacs_language_SummaryProvider(valobj, internal_dict, options):
    lan_name = valobj.GetValueForExpressionPath('.rep.lan_name')
    return lan_name

def texmacs_space_SummaryProvider(valobj, internal_dict, options):
    min_val = valobj.GetValueForExpressionPath('.rep.min').signed
    def_val = valobj.GetValueForExpressionPath('.rep.def').signed
    max_val = valobj.GetValueForExpressionPath('.rep.max').signed
    return f'min={min_val},def={def_val},max={max_val}'


def texmacs_string_SummaryProvider(valobj, internal_dict, options):
    n = valobj.GetValueForExpressionPath('.rep.n').signed
    if n == 0:
        return ""
    s = ""
    for i in range(n):
        val = valobj.GetValueForExpressionPath('.rep.a' + '[' + str(i) + ']').unsigned
        s += chr(val)
    return s

def __lldb_init_module (debugger, dict):

    debugger.HandleCommand("""type synthetic add -x "^array<.*>$" --python-class texmacs.texmacs_array_SyntheticChildrenProvider -w texmacs""")
    debugger.HandleCommand('type summary add -x "^hashmap<.*,.*>$" -F texmacs.texmacs_hashmap_SummaryProvider -w texmacs')
    debugger.HandleCommand('type summary add -x "^array<.*>$" --summary-string "size=${svar%#}" -w texmacs')
    debugger.HandleCommand("""type synthetic add -x "^list<.*>$" --python-class texmacs.texmacs_list_SyntheticChildrenProvider -w texmacs""")
    debugger.HandleCommand('type summary add -x "^list<.*>$" --summary-string "size=${svar%#}" -w texmacs')


    debugger.HandleCommand('type summary add -x "rectangles" --summary-string "size=${svar%#}" -w texmacs')
    
    # Sometimes, texmacs string is not end with \0
    # So, this command is not suitalbe
    # debugger.HandleCommand('type summary add string --summary-string "${var.rep.a}"')
    # add another texmacs_string_SummaryProvider to print string

    type_list = [
        'string',
        'rectangle',
        'xkerning',
        'font',
        'pencil',
        'qt_proxy_renderer_rep',
        'box_rep',
        'brush',
        'no_brush_rep',
        'path',
        'basic_character',
        'coord2',
        'language',
        'space'
    ]
    for item in type_list:
        debugger.HandleCommand(f'type summary add "{item}" -F texmacs.texmacs_{item}_SummaryProvider -w texmacs')
    debugger.HandleCommand("type category enable texmacs")