from segments import Tokenizer, Profile
from karipona import datapath, proto_languages
from writio import load

transliterators = {"transliterate": {}, "tokenize": {}}
extra = ["+", "-", "(", ")", "/", "∅", "0", "?", ",", "=", ";"]
for profile in (datapath / "orthographies").iterdir():
    if profile.suffix != ".csv":
        continue
    pdf = load(profile)
    transliterators["transliterate"][profile.stem] = Tokenizer(
        Profile(
            *(pdf.to_dict("records") + [{"Grapheme": x, "IPA": x} for x in extra])
        )
    )
    transliterators["tokenize"][profile.stem] = Tokenizer(
        Profile(
            *(
                [{"Grapheme": x, "IPA": x} for x in set(pdf["IPA"])]
                + [{"Grapheme": x, "IPA": x} for x in extra]
            )
        )
    )


for plang in proto_languages:
    if plang not in transliterators:
        transliterators["transliterate"][plang] = transliterators["transliterate"]["generic"]
        transliterators["tokenize"][plang] = transliterators["tokenize"]["generic"]
for pemdia in ["tau", "kam"]:
    transliterators["transliterate"][pemdia] = transliterators["transliterate"]["pem"]
    transliterators["tokenize"][pemdia] = transliterators["tokenize"]["pem"]


diphthong_profiles = ["mac", "apa", "tau", "aka"]
wvowels = ["a", "e", "i", "o", "ə", "ɨ"]
def fix_diphthongs(s, mode="transliterate"):
    if mode=="transliterate":
        for v in wvowels:
            s = s.replace(f"{v}u", f"{v}w")
    elif mode=="tokenize":
        for v in wvowels:
            s = s.replace(f"{v} u", f"{v} w")
    else:
        raise ValueError(mode)
    return s


def convert(string, profile, warn=True, **kwargs):
    if profile in diphthong_profiles:
        string = fix_diphthongs(string)
    res = transliterators["transliterate"][profile](string, column="IPA", **kwargs)
    if "�" in res and warn:
        print(string, res)
    return res


def ipaify(string, profile, warn=True, convert_ipa=True):
    if convert_ipa:
        return convert(string, profile, warn, segment_separator="", separator=" ")
    else:
        return tokenize_ipa(string, profile, segment_separator="", separator=" ")


def tokenize_ipa(string, profile, **kwargs):
    res = transliterators["tokenize"][profile](string, **kwargs)
    if profile in diphthong_profiles:
        res = fix_diphthongs(res, mode="tokenize")
    return res


def tokenize(string, profile, convert_ipa=True, warn=True):
    if convert_ipa:
        return convert(string, profile, warn)
    else:
        return tokenize_ipa(string, profile)