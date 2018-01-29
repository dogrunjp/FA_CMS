import sys
from jinja2 import Environment, FileSystemLoader, Markup
from oauth2client.service_account import ServiceAccountCredentials
from collections import defaultdict, Counter
from datetime import datetime as dt
import argparse
import gspread
import json
import csv
import yaml
import os
import urllib
import markdown
import time
import itertools
import re
from feedgenerator import Rss201rev2Feed as Feed

__version__ = "0.2.0"
config_yaml = "./conf/config.yaml"


class Update:
    def __init__(self, wks_conf):
        self.wks = wks_conf

    def add_contents(self):
        template = self.wks['template']
        required = self.wks['require']
        wks_num = self.wks['num']
        wks_id = self.wks['id']
        static_file = self.wks['static_file']
        summary_file = self.wks['summary_file']
        name = self.wks['file_name_column']
        file_path = self.wks['file_path']

        # コンテンツ取得
        update_item_list = UpdateItemList()
        current_list = update_item_list.get_list(wks_num, required)

        # 更新対象のidリスト生成
        get_diffs = GetDiffs()
        list_diffs = get_diffs.update(current_list, wks_id, static_file)

        # コンテンツリストを最後に更新する
        update_file = UpdateFile()
        update_file.update(current_list, static_file, summary_file, required)

        """
        # tagリストを取得
        get_pic_tagmember = GetPicTagMember()
        tag_list = get_pic_tagmember.get_create_taglist()
        pg_category_list = get_pic_tagmember.create_category_list()
        """

        # レンダリングするコンテンツを生成
        contents = self.filter_contents(current_list, list_diffs)

        # コンテンツページをレンダリング＆ファイルに保存
        render_page = RenderPage()  # HTMLをレンダリング＆ファイル生成
        render_page.render(contents, template, name, file_path)

        #render_page.render_gallery(item_list, list_diffs, tag_list)
        #render_page.render_list(pg_category_list)

    def filter_contents(self, contents, diffs):
        wks_id = self.wks['id']
        # 差分のIDリストを参照して差分のコンテンツリストを生成する
        new_contents = [x for x in contents if x[wks_id] in filter(lambda s:s != "", diffs)]
        return new_contents


class UpdateItemList:
    def get_list(self, wks_num, required):
        records = self.contentAsJson(conf["spreadsheet"], wks_num)

        # 必須条件の設定
        # 必須条件を複数設定できる実装を検討する boolを返す関数を設定すれば良いかも
        records = [x for x in records if is_not_empty(x, required)]

        # tagなどリスト化する必要のある値はtemplateとtemplate filterで対応する
        '''
        for article in records:
            article['tag'] = convert_string2list(article['tag'])
            article['tax_id'] = str(article['tax_id'])
        '''
        return records

    def contentAsJson(self, title, ws):
        wks_num = ws
        scope = ['https://spreadsheets.google.com/feeds/']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(conf['jsonkey'], scope)
        gc = gspread.authorize(credentials)
        sht = gc.open(title)
        wks = sht.get_worksheet(wks_num)
        li = wks.get_all_records()
        return li


class UpdateFile:  #静的コンテンツリスト・コンテンツサマリの更新
    def update(self, pg_list, static_file, summary_file, required):
        with open(conf["static_list_path"]+ "/" + static_file, "w") as f:
            json.dump(pg_list, f, ensure_ascii=False)

        summary_list = []
        for dct in pg_list:
            # 必要項目が空欄でないかチェック
            dct = {k: v for k, v in dct.items() if k in required}
            summary_list.append(dct)

        with open(conf["output_path"]+ "/" + summary_file, "w") as f:
            json.dump(summary_list, f, ensure_ascii=False)


class GetDiffs:
    def update(self, current_list, wks_id, static_file):
        previous_list = []
        try:
            with open(conf["static_list_path"]+ "/" + static_file, "r") as f:
                jsondata = json.load(f)
            previous_list = []  # 前回までに登録したitemのidリストを、前回の更新時保存済みのコンテンツJSONファイルより追加

            for item in jsondata:
                id = item[wks_id]
                previous_list.append(id)
        except IOError:
            previous_list = []


        new_list = []  # 新規に読み込んだidのリスト
        update_list = [] # update flag付きitemのid。この２つのidリストが更新対象
        for item in current_list:
            id = item[wks_id]
            new_list.append(id)  # new_listに現在のspreadsheetの全idを追加
            if item['update']:
                update_list.append(id)  # update_listに現在のspreadsheetのup dateフラグ付きのidを追加

        set_update = set(new_list) - (set(previous_list) - set(update_list))  # 新規に登録された行、またはフラグ付きの行のidセット
        list_diffs = list(set_update)
        list_diffs = filter(lambda s: s != "", list_diffs)
        return list(list_diffs)


class RenderPage:
    def __init__(self):
        # アノテーションする単語のリストを取得
        self.keywords = get_keywords(conf)
        # 正規表現パターンをコンパイル
        self.match_list = create_regex_pattern(self.keywords)

    def render(self, contents, template, name, path):
        env = Environment(loader=FileSystemLoader(conf["template_path"], encoding="utf8"))
        env.filters['format_tag'] = format_tag  # 空白文字除去のためのテンプレートフィルターを定義

        if len(contents) != 0:
            for entry in contents:
                entry["filename"] = entry[name]
                figs = {}
                for i in range(1,5):
                    figs["fig"+str(i)] = {"caption": entry["Fig{}_caption".format(str(i))], "img": entry["Fig{}_jpg".format(str(i))]}

                doc = split_entry(entry["Post_Content"])
                txt = doc[2]
                pat = "\[hs_figure id=(\d)"
                match = re.findall(pat, txt)
                body = multiple_replace(txt, match, figs, path)

                # itemの本文にself.keywordsに一致する単語があればマークアップする。
                # マークアップ箇所のDOMのクラスは conf.annotation.class
                body = add_tag(body, self.match_list)

                # 分解した記事を結合
                entry["Post_Content"] = doc[0] + doc[1] + body + doc[3] + doc[4]

                tmpl = env.get_template(template)
                htm = tmpl.render(item=entry)
                write_static_file(entry, htm)


"""
def render_gallery(self, picture_list, list_diffs, tag_list):
    # pictures = [x["original_png"]for x in picture_list]
    if len(list_diffs):
        picture_info = []
        for item in picture_list:
            picture_dict = {k: v for k, v in item.iteritems() if k in ["original_png", "picture_id", "doi", "title_jp", "title_en", "tag", "apng"]}
            # picture_dictに新規更新分のコンテンツであればnewフラグを追加する{is_new: true}
            if picture_dict["picture_id"] in list_diffs:
                picture_dict["is_new"] = True

            if picture_dict["apng"] != '':
                picture_dict["apng"] = True

            picture_info.append(picture_dict)

        env = Environment(loader=FileSystemLoader(conf["template_path"], encoding="utf8"))
        env.filters["list2string"] = list2string
        template = conf["template"]["picture_gallery"]
        tmpl = env.get_template(template)
        htm = tmpl.render(item=picture_info, tags=tag_list).encode("utf-8")  # コンテンツの情報とタグリストを渡す。
        gallery_info = {}
        gallery_info["filename"] = "pics"
        WriteStaticFile(gallery_info, htm)

def render_list(self, pg_list):
    categories = conf["picture_category"]
    env = Environment(loader=FileSystemLoader(conf["template_path"], encoding="utf8"))
    template = conf["template"]["picture_list"]
    tmpl = env.get_template(template)
    htm = tmpl.render(item=pg_list, cats=categories).encode("utf-8")
    picture_list = {}
    picture_list["filename"] = "picture_list"
    WriteStaticFile(picture_list, htm)
"""


class GetPicTagMember:
    def get_create_taglist(self):
        item_tags = []
        with open(conf['static_list_path'] + "/" + conf["picture_gallery_list"], "r") as f:
            contentdata = json.load(f)
        for item in contentdata:
            if item:
                item_tags.append({"picture_id": item["picture_id"], "tags": item["tag"]})

        dct = defaultdict(list)
        tag_list = []
        tag_list_icon = []
        for item in item_tags:
            if item["picture_id"] != "":
                if "生物アイコン" in item["tags"]:
                    for tag in item["tags"]:
                        if len(tag) > 1:
                            tag = tag.strip()
                            dct[tag].append({"picture_id": item["picture_id"]})
                            tag_list_icon.append(tag)
                else:
                    for tag in item["tags"]:
                        if len(tag) > 1:
                            tag = tag.strip()
                            dct[tag].append({"picture_id": item["picture_id"]})
                            tag_list.append(tag)

        tag_list = list(set(tag_list))
        tag_list_icon = list(set(tag_list_icon))
        tag_list.extend(tag_list_icon)

        with open(conf["output_path"] + "/" + conf["picture_tag"], "w") as f:
            json.dump(dct, f, ensure_ascii=False)

        return tag_list

    def create_category_list(self):
        category_names = conf["picture_category"]
        with open(conf["static_list_path"] + "/" + conf["picture_gallery_list"], "r") as f:
            jsondata = json.load(f)

        pg_category_list = {}
        for item in category_names:
            sub_list = [{"title": x["title_jp"], "uri": x["doi"]} for x in jsondata if item in x["tag"]]
            pg_category_list[item] = sub_list

        return pg_category_list


def write_static_file(item, htm, path="output_path"):
    FA_URL = item["FA_URL"]
    filename = FA_URL.split("/")[-1]
    # this line(if filename~) is necessary for togotv filename extraction
    '''
    if filename.find("http") > -1:
        filename = filename.split("/")[-1].replace(".html#p01", "")
        filename = filename.replace(".html","")
    '''
    with open(conf[path] + "/" + str(filename) + ".html", 'w') as f:
        f.write(htm)


# feedformatterからfeedgeneratorに変更した
class CreateRss:
    def __init__(self):
        rss = []
        today = (dt.today()).strftime('%Y-%m-%d')
        feed = Feed(
            title = '記事タイトル',
            link = 'http://www.example.com/news/',
            feed_url = 'http://www.example.com/news/rss',
            description = '記事の説明'
        )
        feed.add_item()


def is_not_empty(item, lists):
    return all(item[k] != '' for k in lists)


def convert_string2list(s):
    l = [x.strip() for x in (s).split(",")]
    return l


def format_tag(str):
    return str.strip()


def format_datetime(date):
    ymd = str(date)
    dtymd = dt.strptime(ymd, '%Y%m%d')
    return dtymd.strftime('%Y-%m-%d')


def format_replace_period(id):
    id_uri = id.replace(".", "")
    return id_uri


def get_keywords(cf):
    update_item_list = UpdateItemList()
    wks_num = cf['annotation']['wks']['num']
    word_lst = update_item_list.contentAsJson(conf['spreadsheet'], wks_num)
    words = word_filter(word_lst)
    return words


# タグ付けする単語リストを返す
def word_filter(lst):
    lst = [x['用語(FA見出し語)'] for x in lst if x['文字数'] != 1 and x['文字数'] != 2]
    return lst


# アノテーションタグを付加する
def add_tag(txt, m_lst):
    for p in m_lst:
        rep = r'<a href="#" class="anno">\g<0></a>'
        cnt = conf["annotation"]["repl_count"]
        txt = p.sub(rep, txt, count=cnt)
    return txt


def create_regex_pattern(lst):
    pttns = [re.compile(x) for x in lst]
    return pttns


def multiple_replace(st, match, fig, path):
    txt = st
    if match:
        for i in match:
            # group()を利用してidを抽出することができる。
            # 置き換えはidが一致する部分のみ
            pat = "\[hs_figure id={}.+fig{}-caption-text\]".format(i, i)

            tmp = '''
                        <div id="figure{id_num}" class="hs-figure">
                            <div class="hs-figure-box">
                                <a class="highslide" title="$(fig1-caption-text)" onclick="return hs.expand(this, {{captionText: document.getElementById('fig{id_num}-caption-text').innerHTML}})" href="{file_path}/{fig}" target="_blank">
                                    <img src="{file_path}/{fig}" alt="figure{id_num}" width="200px" />
                                </a>
                            </div>
                            <div id="fig{id_num}-caption" class="hs-figure-caption"></div>
                        </div>

                        <script type="text/javascript">document.getElementById('fig{id_num}-caption').innerHTML = document.getElementById('fig{id_num}-caption-text').innerHTML;</script>
                        <div style='clear:both;'></div>
                        '''

            file_path = path

            f = fig["fig{}".format(i)]["img"]
            txt = re.sub(pat, tmp.format(id_num=i, file_path=file_path, fig=f), txt)

        return txt
    else:
        return st


def split_entry(s):
    sep_1 = "<h2>要 約</h2>"
    sep_2 = "<h2>文 献</h2>"
    block_1 = s.partition(sep_1)
    head = block_1[0]
    block_2 = block_1[2].partition(sep_2)
    body = block_2[0]
    foot = block_2[2]
    return [head, sep_1, body, sep_2, foot]


def list2string(list):
    str = ','.join(list)
    return str


def update_controller():
    f = open(config_yaml, 'r')
    global conf
    conf = yaml.load(f)
    f.close()

    # config.yamlに複数のwksが登録されていた場合処理を繰り返す
    for k, v in conf['wks'].items():
        update = Update(v)
        update.add_contents()


if __name__ == "__main__":
    update_controller()

