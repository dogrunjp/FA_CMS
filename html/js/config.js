var parser = {
    "dbpedia": function (d) {
        return [d.slice(d)]
    },
    "sparql": function (d) {
        return d["results"]["bindings"];
    },
    "link": function (d) {
        return d
    }
};


var cards = [
    {
        "dbname": "refex",
        "request_type": "link",
        "title": function (kw) {
            var base_url = "https://refex.dbcls.jp/genelist.php?gene_name%5B%5D=";
            return '<div class="hc-lines"><h3><a href=' + base_url+kw + ' target="_blank">  RefExでこの遺伝子の発現パターンを調べる</a></h3></div>'
        },
        "get_url": function () {
            return []
        },
        "ajax_conf": {"type": "GET", "dataType": "text"},
        "views": "",
        "max_lines": 1
    },
        {
        "dbname": "ggrna",
        "request_type": "link",
        "title": function (kw) {
            var base_url = "https://ggrna.dbcls.jp/ja/";
            return '<div class="hc-lines"><h3><a href=' + base_url+kw + ' target="_blank">  GGRNAでこの遺伝子の情報を検索する</a></h3></div>'
        },
        "get_url":function () {
            return []
        },
        "ajax_conf": {"type": "GET", "dataType": "text"},
        "views": "",
        "max_lines": 1
    },
    {
        "dbname": "uniprot",
        "request_type": "link",
        "title": function (kw) {
            var base_url = "https://www.uniprot.org/uniprot/";
            return '<div class="hc-lines"><h3><a href=' + base_url+kw + ' target="_blank">  UniProtのエントリ' + kw + 'を表示する </a></h3></div>'
        },
        "get_url":function () {
            return []
        },
        "ajax_conf": {"type": "GET", "dataType": "text"},
        "views": "",
        "max_lines": 1
    },
    {
        "dbname": "fa",
        "request_type": "sparql",
        "title": function () {
            return "<h3>このキーワードを含むその他のエントリー</h3>"
        },
        "get_url": function (kw) {
            return 'http://navi.first.lifesciencedb.jp/fanavi/servlet/query?query=PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX%20aos%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fao%2Fselectors%2F%3E%0D%0APREFIX%20doco%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fspar%2Fdoco%2F%3E%0D%0A%0D%0ASELECT%20distinct%20%3Fid%20%3Fo%20%3Ft%20WHERE%20%7B%0D%0A%20%20GRAPH%20%3Chttp%3A%2F%2Fpurl.jp%2Fbio%2F10%2Flsd2fa%3E%20%7B%0D%0A%20%20%20%20%3Fstc%20%5Edoco%3AisContainedBy%20%2F%20aos%3Aexact%20%3Fo%20.%0D%0A%20%20%20%20VALUES%20%3Fo%20%7B%22' + kw + '%22%40ja%7D%0D%0A%20%20%7D%0D%0A%20%20BIND(%20replace(str(%3Fstc)%2C%22article%2F(%5C%5Cd%2B).*%22%2C%22article%2F%241%22)%20as%20%3Fdocidstr%20)%0D%0A%20%20BIND(%20IRI(%3Fdocidstr)%20as%20%3Fdocid%20)%0D%0A%20%20BIND(%20strafter(%3Fdocidstr%2C%20%22article%2F%22)%20as%20%3Fid%20)%0D%0A%20%20%3Fdocid%20rdfs%3Alabel%20%3Ft%20.%0D%0A%7D&format=JSON&limit=25&offset=0&inference=false';
        },
        "ajax_conf": {"type": "GET", "dataType": "json"},
        "views": function (kw, c) {
            // url
            var l = c["id"]["value"];
            // コンテンツのタイトル
            var n = c["t"]["value"];
            return '<div class="hc-lines"><a href='+ l +'>' + n + '</a></div>'
        },
        "max_lines": 5
    }
];
