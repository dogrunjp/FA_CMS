# 新着論文レビュー開発ノート

## はじめに

- 新着論文レビュー(2018version)は領域融合レビューで先行して採用した
google docs原簿システム（docsからpythonで静的ファイル生成＋GASによる検索システム）を
移植して構築する

- すでに原簿システムによる試作は行なっているのでこのバージョンでは下記項目の作業を主に行う
    - LAで使ったテンプレートの利用
    - GASによる検索システム構築（これもLAを参考に）
    - 静的ページの移植
    

## 共通ヘッダフッタ
<body>タグ直下に置くが
</body>タグの直前に置いた方が良い場合もあった（riot.jsとの関係で）

```Javascript
<script type="text/javascript" src="https://dbcls.rois.ac.jp/DBCLS-common-header-footer/common-header-and-footer/script/common-header-and-footer.js" style="display: block" id="common-header-and-footer__script" data-page-type="2.1"></script>

```

## GAS 

- 本番環境用 API
https://script.google.com/macros/s/AKfycbxRUrpftHbs62tP7PFas6Kvd6quoNw_CazWSlTOAOV76fW8f05Z/exec

- 開発用api
https://script.google.com/macros/s/AKfycbybvEaD8OBLQ70O29Ro-aUfptB6iQTEZoXc-pRMZcsOHSb7t3M/exec



## S3

テストサイト用のバケットと同期する

```
aws s3 sync html/ s3://fa.bmu.jp --profile fa-bmu-jp --content-type "text/html"
aws s3 sync s3://leading.lifesciencedb.jp/d3 --profile la-s3
```

バケットから特定のファイルを削除する

```
aws s3 rm s3://fa.bmu.jp/{file name} d3 --profile la-s3
```

## wordpress file passの置き換え

Download link や画像パスはlifesciencedbを指すようにする

http://first.lifesciencedb.jp/wordpress/wp-content/uploads/2018/08/Eto-Cell-18.7.12-Fig.1.jpg
これは
https://dbarchive.biosciencedbc.jp/data/first_authors/data/Fig/Eto-Cell-18.7.12-Fig.1.jpg

## gitのリモートからのみファイルを削除する

- git rm --cached hoge.json
- git add -u
- git commit -m "delete some file"
- git push origin master

# gitの履歴を削除する

- 指定したファイルを消す
git filter-branch --tree-filter "rm -f [消したいファイルパス]" HEAD

- 指定したディレクトり以下を消す
git filter-branch --tree-filter "rm -f -r [消したいディレクトリパス] " HEAD

- リポジトリを最適化
git gc --aggressive --prune=now

で、git push -f

[Git リポジトリに上がっているファイルを履歴ごと消すには？](https://qiita.com/go_astrayer/items/6e39d3ab16ae8094496c)


## jinja2で定義されるリストを複数回テンプレートで使いたい場合

{% block hoge %}{% endblock %} はイテレータであるため、複数回使うのは無理。
直接この変数を使うのではなく別の変数に代入して使えば良い