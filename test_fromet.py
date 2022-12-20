# tests for the construct xml fromET stuff

import pytest

from cons_xml import *
from cons_utils import *


def test_formatfield():
    T = Int32ul
    ctx = {}
    parent = ET.Element("parent")
    parent.attrib["foo"] = "4"
    ctx, size = T.fromET(context=ctx, parent=parent, name="foo")
    assert (size == 4)
    assert (ctx["foo"] == 4)

    ctx = {"foo": [2]}
    ctx, size = T.fromET(context=ctx, parent=parent, name="foo")
    assert (size == 4)
    assert (ctx["foo"] == [2, 4])


def test_renamed():
    T = "test" / Int32ul
    ctx = {"teststuff": "someparentstuff"}
    parent = ET.Element("parent")
    parent.attrib["test"] = 4
    ctx, size = T.fromET(context=ctx, parent=parent, name="foo")
    assert (size == 4)
    assert (ctx["teststuff"] == "someparentstuff")
    assert (ctx["test"] == 4)

    pass


def test_struct_formatfields():
    T = Struct(
        "a" / Int32ul,
        "b" / Float32l,
    )

    ctx = {"test": "someparentstuff"}

    parent = ET.Element("parent")
    struct = ET.Element("teststruct")
    struct.attrib["a"] = "3"
    struct.attrib["b"] = "4.6"
    parent.append(struct)

    ctx, size = T.fromET(context=ctx, parent=parent, name="teststruct", offset=56)
    assert (size == 8)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["teststruct"]["a"] == 3)
    assert (ctx["teststruct"]["b"] == 4.6)
    assert (ctx["teststruct"]["_offset"] == 56)
    assert (ctx["teststruct"]["_size"] == 8)
    assert (ctx["teststruct"]["_endoffset"] == 64)
    assert (ctx["teststruct"]["_"]["test"] == "someparentstuff")


def test_struct_root():
    T = Struct(
        "a" / Int32ul,
        "b" / Float32l,
    )

    ctx = {"test": "someparentstuff"}

    struct = ET.Element("teststruct")
    struct.attrib["a"] = "3"
    struct.attrib["b"] = "4.6"

    ctx, size = T.fromET(context=ctx, parent=struct, name="teststruct", offset=56, is_root=True)
    assert (size == 8)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["a"] == 3)
    assert (ctx["b"] == 4.6)
    assert (ctx["_offset"] == 56)
    assert (ctx["_size"] == 8)
    assert (ctx["_endoffset"] == 64)
    assert (ctx["_"]["test"] == "someparentstuff")


def test_struct_nested():
    T = Struct("foo" / Int32ul,
               "newname" / Struct(
                   "a" / Int32ul,
                   "b" / Float32l,
               ),
               "bar" / Int32ul,
               )

    ctx = {"test": "someparentstuff"}

    parent = ET.Element("parent")
    subparent = ET.Element("teststruct")
    subparent.attrib["foo"] = "12"
    struct = ET.Element("newname")
    struct.attrib["a"] = "3"
    struct.attrib["b"] = "4.6"
    subparent.attrib["bar"] = "13"
    subparent.append(struct)
    parent.append(subparent)

    print(ET.tostring(parent).decode("utf-8"))

    ctx, size = T.fromET(context=ctx, parent=parent, name="teststruct", offset=56)
    assert (size == 16)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["teststruct"]["newname"]["a"] == 3)
    assert (ctx["teststruct"]["newname"]["b"] == 4.6)
    assert (ctx["teststruct"]["_offset"] == 56)
    assert (ctx["teststruct"]["_size"] == 16)
    assert (ctx["teststruct"]["_endoffset"] == 72)
    assert (ctx["teststruct"]["_"]["test"] == "someparentstuff")


def test_array_formatfields():
    T = Array(4, Int32ul)

    parent = ET.Element("parent")
    child = ET.Element("testarray")
    child.text = "4,3,2,1"
    parent.append(child)
    ctx = {"test": "someparentstuff"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="testarray", offset=12)
    assert (size == 16)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["testarray"] == [4, 3, 2, 1])


# named formatfields in arrays should be ignored
def test_array_formatfields():
    T = Array(4, "foobar" / Int32ul)

    parent = ET.Element("parent")
    child = ET.Element("testarray")
    child.text = "4,3,2,1"
    parent.append(child)
    ctx = {"test": "someparentstuff"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="testarray", offset=12)
    assert (size == 16)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["testarray"] == [4, 3, 2, 1])


def test_array_struct():
    T = Struct("foo" / Int32ul,
               "arr" / Array(4, Int32ul),
               "bar" / Int32ul,
               )
    parent = ET.Element("parent")
    child = ET.Element("teststruct")
    arr = ET.Element("arr")
    arr.text = "1,2,3,4"
    child.attrib["foo"] = "2"
    child.attrib["bar"] = "4"
    child.append(arr)
    parent.append(child)
    ctx = {"test": "someparentstuff"}
    ctx, size = T.fromET(context=ctx, parent=parent, name="teststruct", offset=12)
    assert (size == 6 * 4)
    assert (ctx["test"] == "someparentstuff")
    assert (ctx["teststruct"]["_size"] == size)
    assert (ctx["teststruct"]["_offset"] == 12)
    assert (ctx["teststruct"]["_endoffset"] == size + 12)
    assert (ctx["teststruct"]["arr"] == [1, 2, 3, 4])
