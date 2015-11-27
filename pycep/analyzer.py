from __future__ import absolute_import
import parser
import pycep.parser

def parse(source):
    # TODO: this is a stub
    st = pycep.parser.suite(source)
    ast = parser.sequence2ast(st.tolist())

    return ast