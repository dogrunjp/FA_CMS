# coding: utf-8

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
import subprocess
# CreateRssで利用するが現在不使用
# from feedgenerator import Rss201rev2Feed as Feed
from bs4 import BeautifulSoup
from ahocorapy.keywordtree import KeywordTree
import add_annotation

__version__ = "0.3.0"
config_yaml = "./conf/config.yaml"

parser = argparse.ArgumentParser(description='how to use puppy')
parser.add_argument('--sync', '-s', dest='sync',action='store_true', help='sync html files')
parser.add_argument('--update', '-u', dest='update',action='store_true', help='create files')
parser.add_argument('--binary', '-b', dest='binary',action='store_true', help='sync binary files')
parser.add_argument('--list', '-l', dest='list',action='store_true', help='create contents list')
args = parser.parse_args()


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
        img_path = self.wks['img_path']
        menu_template = self.wks['menu_template']

        # コンテンツ（ワークシートの全データjson）取得
        update_item_list = UpdateItemList()
        current_list = update_item_list.get_list(wks_num, required)

        # 更新対象のidリスト生成
        get_diffs = GetDiffs()
        list_diffs = get_diffs.update(current_list, wks_id, static_file)

        # コンテンツリストを最後に更新する
        update_file = UpdateFile()
        update_file.update(current_list, static_file, summary_file, required)

        # レンダリングするコンテンツを生成
        contents = self.filter_contents(current_list, list_diffs)

        # コンテンツページをレンダリング＆ファイルに保存
        render_page = RenderPage()  # HTMLをレンダリング＆ファイル生成
        render_page.render(contents, template, name, file_path, img_path, self.wks)

        # drawer-navに表示するcustom tagを書き出す
        render_menu_list(current_list, menu_template)

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
        scope = ['https://spreadsheets.google.com/feeds/',
                 'https://www.googleapis.com/auth/drive']
        # versionによっては（ubuntu 最新のauth）以下のようにscoprを設定する必要がある
        # scope = ['https://spreadsheets.google.com/feeds',
        # 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(conf['jsonkey'], scope)
        gc = gspread.authorize(credentials)
        sht = gc.open(title)
        wks = sht.get_worksheet(wks_num)
        li = wks.get_all_records()
        return li


# 静的コンテンツリスト・コンテンツサマリの更新
class UpdateFile:
    def update(self, pg_list, static_file, summary_file, required):
        with open(conf["static_list_path"] + static_file, "w") as f:
            # json.dump(pg_list, f, ensure_ascii=False)
            # 環境によてensure_asciiをtrueにした方が良い場合とそうで無い場合がある
            json.dump(pg_list, f)

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
            with open(conf["static_list_path"]+ "/" + static_file, "r", encoding='utf-8') as f:
                #print(conf["static_list_path"]+ "/" + static_file)
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
        # アノテーションするFA_ID&単語のセットのリストを取得
        self.keywords = get_keywords(conf)

    def render(self, contents, template, name, path, img_p, wks_conf):
        env = Environment(loader=FileSystemLoader(conf["template_path"], encoding="utf8"))
        env.filters['format_tag'] = format_tag  # 空白文字除去のためのテンプレートフィルターを定義
        if len(contents) != 0:
            for entry in contents:
                entry["filename"] = entry[name]
                figs = {}
                # figureの設定
                # 登録されたFigureの数を取得
                l = []
                for k, v in entry.items():
                    if (k.endswith('_jpg')):
                        l.append(v)
                l = list(filter(lambda x:x != '' , l))
                len_lst = len(l)

                for i in range(1, len_lst + 1):
                    figs["fig"+str(i)] = {"caption": entry["Fig{}_caption".format(str(i))], "img": entry["Fig{}_jpg".format(str(i))]}

                # 本文（entry["post_content"]）を<要約＞パート、<文献＞パートで分割する。本文部分doc[2]をtxtに代入。
                doc = split_entry(entry["Post_Content"])
                txt = doc[2]
                # Annotationしない場合はコンテンツ全体を取得
                #txt = entry["Post_Content"]

                # リストcapsの長さがfigの数としてFigureのcaptionを取得
                caps = [entry.get("Fig{}_caption".format(i)) for i in range(1, 4) if entry.get("Fig{}_caption".format(i), None) != ""]

                # 画像のキャプションを一時的に<tmp>タグに置き換える
                soup = BeautifulSoup(txt, "html.parser")
                captions = []
                for i in range(len(caps)):
                    idx = i + 1
                    try:
                        captions.append(soup.find(id="fig{}-caption-text".format(idx)))
                        soup.find(id="fig{}-caption-text".format(idx)).replace_with("tmp_fig{}".format(idx))
                    except:
                        pass
                txt = str(soup)

                # Hover card用のannotation追加
                # keywordsはFA_URLの数字部分(FA_IDではなく)と一致するセットだけフィルターして渡す。また削除フラグに1が入っていた場合その語は使用しない。
                keyword_work = [(x[1], x[2], x[3]) for x in self.keywords if str(x[0]) == str(entry["FA_URL"].split("/")[-1])]
                uniprot_ids = [x[2] for x in keyword_work if x[2]]
                entry["uniprotids"] = uniprot_ids

                # htmlにアノテーションのためのタグを付加
                txt = add_annotation.add_annotation(keyword_work, txt)

                # 一時置換したタグをリストcaptionsから復元する
                for i in range(len(caps)):
                    idx = i + 1
                    txt = re.sub("tmp_fig{}".format(idx), str(captions[i]), txt)

                # 画像部分のテキストをHTMLに置き換え
                body = replace_figures(txt, figs, path, img_p, caps)

                doc_genes = ""
                if len(keyword_work) != 0:
                    doc_genes = """
                    <h2>この論文に出現する遺伝子・タンパク質のUniprot ID</h2>
                        <div class="gene_list">
                        {0}
                        </div>
                        <ul class="gene_list">
                        <li><a href="#"dl_uniprot_ids" id="dl_uniprot_ids">Uniprot ID一覧をテキストファイルでダウンロードする</a></li>
                        <li><a href="#copy_uniprot_ids" id="copy_uniprot_ids">Uniprot ID一覧をクリップボードにコピーする</a></li>
                        <li><a href="https://togoid.dbcls.jp/">TogoIDで関連するIDを変換する</a></li>
                        </ul>
                        <div><form>
                        <div class="selected_list"><input type="checkbox" id="prop" class="selected_db" name="targetdb" value="refex" checked> キーワードをアノテーションする</div>
                        </form></div>
                    """
                    gu_lst = ["{0}(<a href='https://www.uniprot.org/uniprot/{1}'>{1}</a>)".format(x[0], x[2]) if x[2] else "{0}".format(x[0]) for x in keyword_work]
                    gu = ",  ".join(gu_lst)

                    # アノテーションを加えて、分解した記事に遺伝子・Uniprot情報を追加し結合
                    entry["Post_Content"] = doc[0] + doc_genes.format(gu) + doc[1] + body + doc[3] + doc[4]
                else:
                    # アノテーションを加えて、分解した記事をそのまま結合
                    entry["Post_Content"] = doc[0] + doc[1] + body + doc[3] + doc[4]


                # entry["post_content"]にスプレッドシートのextra項目を結合する
                """
                if entry.get("post_content_extra"):
                    entry["post_content"] = entry["post_content"] + entry["post_content_extra"]
                else:
                    pass
                """
                # annotationがあればtemplateにフォームを追加
                # keyword_work がから出ないならばformを追加する。からであるなら空白を追加
                if len(keyword_work) != 0:
                    template = "fa_detail_anno.html"
                else:
                    template = "fa_detail.html"

                # templateを指定
                tmpl = env.get_template(template)
                htm = tmpl.render(item=entry)
                write_static_file(entry, htm, wks_conf["output_path"])


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


def write_static_file(item, htm, path):
    LA_URL = item["FA_URL"]
    filename = LA_URL.split("/")[-1]
    # this line(if filename~) is necessary for togotv filename extraction
    '''
    if filename.find("http") > -1:
        filename = filename.split("/")[-1].replace(".html#p01", "")
        filename = filename.replace(".html","")
    '''
    try:
        with open(path + "/" + str(filename), 'w') as f:
        #with open(conf[path] + "/" + str(filename) + ".html", 'w') as f:
            f.write(htm)
    except:
        print(item)


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
    # スプレッドシートから見出し語データを取得
    word_lst = update_item_list.contentAsJson(conf['spreadsheet'], wks_num)
    # 見出し語をフィルターする
    words = word_filter(word_lst)
    return words


# タグ付けする単語リストを返す
def word_filter(lst):
    """
    col_terms = conf["annotation"]["terms"]
    col_id = conf["annotation"]["page_id"]
    flag = conf["annotation"]["flag"]
    # deplicated
    """

    page_id = conf["annotation"]["page_id"]
    cue = conf["annotation"]["lexical_cue"]
    text_query = conf["annotation"]["text_query"]
    uniprot = conf["annotation"]["uniprot"]
    only_uniprot = conf["annotation"]["only_uniprot"]

    # UniprotIDがあればUniprotID然もなくばOnlyUniProtIDをuniprot_idとして取得する
    uniprot_id  = uniprot if uniprot else only_uniprot
    # uniprotの値はuniprotIDもしくはonly_uniprot_idから
    lst = [(x[page_id], x[cue], x[text_query], x.get(uniprot_id) if x.get(uniprot_id, None) else x.get(only_uniprot)) for x in lst if x[cue]]
    return lst


# アノテーションタグを付加する
def add_tag(txt, m_lst):
    #置き換えリスト
    rep = r'<a href="#" class="anno \g<0>">\g<0></a>'
    cnt = conf["annotation"]["repl_count"]
    for p in m_lst:
        txt = p.sub(rep, txt, count=cnt)
    return txt


def replace_figures(st, fig, path, img_p, caps):
    txt = st

    # [hs_figure]を変換
    pat_hs = "\[hs_figure id=(\d)"
    match_hs = re.findall(pat_hs, txt)
    if match_hs:
        for i in match_hs:
            # group()を利用してidを抽出することができる。
            # 置き換えはidが一致する部分のみ
            pat = "\[hs_figure id={}.+fig{}-caption-text\]".format(i, i)

            tmp = '''
                        <div id="figure{id_num}" class="hs-figure">
                            <div class="hs-figure-box">
                                <a class="highslide" title="{caption}" href="{img_p}{fig}" target="_blank">
                                    <img src="{img_p}{fig}" alt="figure{id_num}" width="200px" />
                                </a>
                            </div>
                            <div id="fig{id_num}-caption" class="hs-figure-caption"></div>
                        </div>

                        <script type="text/javascript">document.getElementById('fig{id_num}-caption').innerHTML = document.getElementById('fig{id_num}-caption-text').innerHTML;</script>
                        <div style='clear:both;'></div>
                        '''

            #file_path = path


            try:
                # fig
                f = fig["fig{}".format(i)]["img"]
                c = caps[int(i) - 1]
                txt = re.sub(pat, tmp.format(caption=c, id_num=i, img_p=img_p, fig=f), txt) # Fig1-caption
            except:
                txt = re.sub(pat, "", txt)

    else:
        txt = txt

    # wordpressのPDFパスの置き換え。画像パスと重なるため、こちらを先に置き換える。
    pdf_path = path + "Doc/"
    pat_pdf_path = "http://first.lifesciencedb.jp/wordpress/wp-content/uploads/\d+/\d+/(.+\.pdf)"

    match_pdf_path = re.findall(pat_pdf_path, txt)
    if match_pdf_path:
        for i in match_pdf_path:
            txt = re.sub(pat_pdf_path, pdf_path +'\g<1>', txt)

    # wordpressの画像パスの置き換え
    pat_wp_path = "http://first.lifesciencedb.jp/wordpress/wp-content/uploads/\d+/\d+/"
    match_wp_path = re.findall(pat_wp_path, txt)
    if match_wp_path:
        for i in match_wp_path:
            txt = re.sub(pat_wp_path , img_p, txt)

    pat_wp_path2 = "http://first.lifesciencedb.jp/wp-content/uploads/\d+/\d+/"
    match_wp_path2 = re.findall(pat_wp_path2, txt)
    if match_wp_path2:
        for i in match_wp_path2:
            txt = re.sub(pat_wp_path2, img_p, txt)

    return txt


# 生成したhtmlファイルをS3とシンクする。Content-type=text/htmlが指定される
def sync_pages(bucket, source, profile):
    b = bucket
    s = source
    p = profile
    command = 'aws s3 sync {s} s3://"{b}" --profile {p} --content-type "text/html"'.format(b=b, s=s, p=p)
    subprocess.call(command, shell=True)


# htmlファイル以外のファイルを更新した際に呼ぶ
def sync_binary(bucket, source, profile):
    b = bucket
    s = source
    p = profile
    command = 'aws s3 sync {s} s3://"{b}" --profile {p}'.format(b=b, s=s, p=p)
    subprocess.call(command, shell=True)


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


def render_menu_list(item, template):
    journal_lst = []
    years = []
    category_lst = []
    for obj in item:
        years.append(obj["Date"].split("/")[0])
        journal_lst.append(obj["OriginalArticle"])
        category_lst.extend([x.strip() for x in obj["Post_Tag"].split(",")])

    lst_journal = []
    # 値でsortするのでitems()では無くmost_common()でタブルのリストを生成する。
    for t in Counter(journal_lst).most_common():
        lst_journal.append({"name": t[0], "val": t[1]})
    dct_journal = {"title": "ジャーナル別", "li": lst_journal, "name": "drawer-journal", "target": "journal"}

    lst_tag = []
    for t in Counter(category_lst).most_common():
        lst_tag.append({"name": t[0], "val": t[1]})
    lst_tag = [x for x in lst_tag if int(x["val"]) >= 10]
    dct_tag = {"title": "タグ別", "li": lst_tag, "name": "drawer-category", "target": "category"}

    lst_year = []
    for t in Counter(years).most_common():
        lst_year.append({"name": t[0], "val": t[1]})
    lst = sorted(lst_year, key=lambda x: int(x["name"]), reverse=True)
    dct_year = {"title": "公開年別", "li": lst, "name": "drawer-date", "target": "date"}

    for obj in [dct_tag, dct_journal, dct_year]:
        env = Environment(loader=FileSystemLoader(conf["template_path"], encoding="utf8"))
        env.filters['format_tag'] = format_tag  # 空白文字除去のためのテンプレートフィルターを定義
        tmpl = env.get_template(template)
        htm = tmpl.render(item=obj, li=obj["li"])

        with open(conf["tag_path"] + obj["name"] + ".tag", 'w') as f:
            f.write(htm)


class CreateList:
    def __init__(self, wks_conf):
        self.wks = wks_conf

    def create_list_page(self):
        required = self.wks['require']
        wks_num = self.wks['num']
        wks_id = self.wks['id']
        img_path = self.wks['img_path']

        env = Environment(loader=FileSystemLoader(conf["template_path"], encoding="utf8"))
        env.filters['format_tag'] = format_tag  # 空白文字除去のためのテンプレートフィルターを定義

        # コンテンツ（ワークシートの全データ）取得
        update_item_list = UpdateItemList()
        current_list = update_item_list.get_list(wks_num, required)
        archive_list = [{"Title": x["Title"], "FA_URL": convert2https(x["FA_URL"])} for x in current_list]

        template = "archive_list.html"
        output_path = "/var/www/fa/"

        # html生成
        tmpl = env.get_template(template)
        htm = tmpl.render(item=archive_list)
        file_name = "list"
        with open(output_path + file_name, "w") as f:
            f.write(htm)


def convert2https(u):
    us = u.replace("http", "https")
    return us


def update_controller():
    f = open(config_yaml, 'r', encoding='utf-8')
    global conf
    conf = yaml.safe_load(f)
    f.close()

    # config.yamlに複数のwksが登録されていた場合処理を繰り返す
    for k, v in conf['wks'].items():
        if args.sync:
            sync_pages(v['bucket'], v['output_source'], v['bucket_profile'])
        elif args.binary:
            sync_binary(v['bucket'], v['output_source'], v['bucket_profile'])
        elif args.list:
            # archive/のコンテンツに対してのみ実行する
            if k == "first":
                create_list = CreateList(v)
                create_list.create_list_page()
        elif args.update:
            update = Update(v)
            update.add_contents()


def test_get_keywords():
    f = open(config_yaml, 'r', encoding='utf-8')
    global conf
    conf = yaml.safe_load(f)
    f.close()
    words = get_keywords(conf)


def test_get_addclass():
    f = open(config_yaml, 'r', encoding='utf-8')
    global conf
    conf = yaml.safe_load(f)
    f.close()
    kws = get_keywords(conf)

    keyword_work = [(x[1], x[2], x[3]) for x in kws if str(x[0]) == "hoge.html.html"]
    txt = """
PD-1やCTLA-4に対する...LAG-3は
PD-1およびCTLA-4に..さまざまな..，
LAG-3が免疫を抑制する..この研究において，筆者らは，LAG-3がMHCクラスII分子複合体を選択的に...
MHCクラスII分子とヘルパーT細胞の活性化を、インスリンB鎖、CD4、CD8、pMHCII
    """
    s = add_annotation.add_class(keyword_work, txt)


def test_kws():
    f = open(config_yaml, 'r', encoding='utf-8')
    global conf
    conf = yaml.safe_load(f)
    f.close()
    kws = get_keywords(conf)
    kws = [(x[1], x[2], x[3]) for x in kws]
    print(kws[0:10])
    for k in kws:
        if len(k) != 3:
            print(k)


if __name__ == "__main__":
    update_controller()


