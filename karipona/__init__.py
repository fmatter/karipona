import itertools
import re

import pybtex
from Bio import Phylo
from importlib_resources import files
from pycldf import Dataset
from pycldf.sources import Source
from writio import load

datapath = files("karipona") / "data"
metadata_path = datapath /"cldf"/"metadata.json"

c_data = Dataset.from_metadata(metadata_path)
sources = pybtex.database.parse_file(c_data.bibpath)
sources = {k: Source.from_entry(k, e) for k, e in sources.entries.items()}

tree = Phylo.read(datapath / "tree.nwk", "newick")


glottocodes = {}
shorthands = {}
lang_ids = {}
isos = {}
dialects = {}
language_data = {}
attested_languages = []
proto_languages = []

for lg in c_data["LanguageTable"]:
    glottocodes[lg["Glottocode"]] = {
        "shorthand": lg["Shorthand"],
        "id": lg["ID"],
        "name": lg["Name"],
    }

    shorthands[lg["Shorthand"]] = {
        "id": lg["ID"],
        "name": lg["Name"],
        "glottocode": lg["Glottocode"],
    }

    lang_ids[lg["ID"]] = {
        "shorthand": lg["Shorthand"],
        "name": lg["Name"],
        "glottocode": lg["Glottocode"],
    }
    language_data[lg["ID"]] = lg

    if lg["Dialect_Of"] != None:
        dialects[lg["ID"]] = lg["Dialect_Of"]
    else:
        dialects[lg["ID"]] = lg["ID"]

    if lg["Proto_Language"]:
        proto_languages.append(lg["ID"])
    else:
        attested_languages.append(lg["ID"])


def iter_nodes(node):
    yield node.name
    for child in node.clades:
        for x in iter_nodes(child):
            yield x


def tree_order():
    return list(iter_nodes(tree.root))


def get_lg_data(id):
    return language_data[id]


def get_glottocode(string):
    for map in [shorthands, lang_ids]:
        if string in map:
            return map[string]["glottocode"]


def get_shorthand(string):
    for map in [glottocodes, lang_ids]:
        if string in map:
            return map[string]["shorthand"]


def get_name(string):
    for map in [glottocodes, shorthands, lang_ids]:
        if string in map:
            return map[string]["name"]


def get_lg_id(string):
    for map in [glottocodes, shorthands, isos]:
        if string in map:
            return map[string]["id"]


def dedialectify(string):
    orig = string
    if string in lang_ids:
        return dialects[string]
    else:
        dialect_id = dialects[get_lg_id(string)]
        if orig in glottocodes:
            return get_glottocode(dialect_id)
        elif orig in shorthands:
            return get_shorthand(dialect_id)


lists = {
    "glottocode": get_glottocode,
    "shorthand": get_shorthand,
    "id": get_lg_id,
    "name": get_name,
}


def lg_order(identifier="id", as_dict=True):
    order = tree_order()
    if identifier != "id":
        order = list(map(lists[identifier], order))
    if as_dict:
        numbers = list(range(0, len(order)))
        return dict(zip(order, numbers))
    else:
        return order

comparative_list = {"PPem": ["aka", "ing", "pat", "tau", "are", "mac"], "Venezuelan": ["PPem", "pan", "yab", "pno", "map", "mak", "cha", "cum"]}

separators = ["-", "=", "<", ">"]


def deparentify(full_string, par="("):
    if par == "(":
        par2 = ")"
    elif par == "[":
        par2 = "]"
    all_variants = []

    def iterate(string):
        for repl in [r"\1", ""]:
            if par == "(":
                variant = re.sub(rf"\((.*?)\)", repl, string, 1)
            elif par == "[":
                variant = re.sub(rf"\[(.*?)\]", repl, string, 1)
            if par in variant:
                for i in iterate(variant):
                    yield i
            else:
                yield variant.replace(par2, "")

    for substring in full_string.split(" / "):
        all_variants.extend(
            list(itertools.chain(*[iterate(s) for s in substring.split(", ")]))
        )
    seen = set()
    return [x for x in all_variants if not (x in seen or seen.add(x))]


def get_cldf_lg_table(lol):
    out = []
    for lg in set(lol):
        out.append(
            {
                your_key: language_data[lg][your_key]
                for your_key in ["ID", "Glottocode", "Name", "Latitude", "Longitude"]
            }
        )
    return out


def split_col(df, col, sep="; "):
    df[col] = df[col].apply(lambda x: x.split(sep))


def join_col(df, col, sep="; "):
    df[col] = df[col].apply(lambda x: sep.join(x))
