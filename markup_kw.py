# coding: UTF-8
import re
from collections import OrderedDict
from ahocorapy.keywordtree import KeywordTree


def create_unique_word_list(kwt):
    dct = {}
    for kw in kwt:
        if not dct.get(kw[0]):
            dct[kw[0]] = kw[1]
    d = OrderedDict(sorted(dct.items(), key=lambda item : len(item[0]), reverse=True))
    return d


def remove_overlapped(dct):
    # ポジションと単語長からキーワードのテキスト中の位置（=レンジ）を生成
    ranged = []
    for k, v in dct.items():
        ranged.append((k,range(v, v + len(k))))

    # 単語長の長いキーワードからkw_rangeに埋められたテキスト内のレンジを登録していく
    kws = []
    kw_range = set()
    for s in ranged:
        # 単語の重なりがある場合
        if set(s[1]).intersection(kw_range):
            pass
        else:
            kws.append(s[0])
            kw_range = kw_range.union(set(s[1]))
    return kws


def create_keywordtree(lst, s):
    kwtree = KeywordTree(case_insensitive=True)
    for w in lst:
        kwtree.add(w)
    kwtree.finalize()
    # (keyword, position)のタプルのリストを返す
    res = kwtree.search_all(s)
    return res


def add_class(kws, txt):
    rep = r'<a href="#" class="anno \1">\1</a>'
    cnt = 1
    for k in kws:
        ptn = '(?!<a[^>]*?>)({})(?![^<]*?</a>)'.format(k)
        txt = re.sub(ptn, rep, txt, count=cnt)
    return txt


def create_regex_pattern(lst):
    # 単語リストからコンパイル済みの正規表現のリストを生成する
    protect = ["dis", "org", "PDF", "arc", "bar", "ank", "pla", "ral", "lec", "seq", "sp1", "Msx"]
    ptn = [re.compile(x) for x in lst if x not in protect]
    return ptn


def add_annotation(kws, txt):
    kwt = create_keywordtree(kws, txt)
    # レンジ被りをのぞいたキーワードリストを生成する。
    w_kws = remove_overlapped(create_unique_word_list(kwt))
    # 重複をのぞいたキーワードリストとテキストを渡す
    s = add_class(w_kws, txt)
    return s

