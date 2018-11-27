var parser = {
    "dbpedia": function (d) {
        return [d.slice(d)]
    },
    "sparql": function (d) {
        return d["results"]["bindings"];
    },
    "link": function (d) {
        return d.slice(d)
    }
};


var cards = [
    {
        "dbname": "refex",
        "request_type": "link",
        "title": function (kw) {
            var base_url = "https://refex.dbcls.jp/genelist.php?gene_name%5B%5D=";
            return `<div class="hc-lines"><h3><a href=${base_url}${kw} target="_blank"> RefExこの遺伝子の発現パターンを調べる</a></h3></div>`
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
            return `<div class="hc-lines"><h3><a href=${base_url}${kw} target="_blank"> GGRNAでこの遺伝子の情報を検索する</a></h3></div>`
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
            return `http://navi.first.lifesciencedb.jp/fanavi/servlet/query?query=PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX%20aos%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fao%2Fselectors%2F%3E%0D%0APREFIX%20doco%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fspar%2Fdoco%2F%3E%0D%0A%0D%0ASELECT%20distinct%20%3Fid%20%3Fo%20%3Ft%20WHERE%20%7B%0D%0A%20%20GRAPH%20%3Chttp%3A%2F%2Fpurl.jp%2Fbio%2F10%2Flsd2fa%3E%20%7B%0D%0A%20%20%20%20%3Fstc%20%5Edoco%3AisContainedBy%20%2F%20aos%3Aexact%20%3Fo%20.%0D%0A%20%20%20%20VALUES%20%3Fo%20%7B%22${kw}%22%40ja%7D%0D%0A%20%20%7D%0D%0A%20%20BIND(%20replace(str(%3Fstc)%2C%22article%2F(%5C%5Cd%2B).*%22%2C%22article%2F%241%22)%20as%20%3Fdocidstr%20)%0D%0A%20%20BIND(%20IRI(%3Fdocidstr)%20as%20%3Fdocid%20)%0D%0A%20%20BIND(%20strafter(%3Fdocidstr%2C%20%22article%2F%22)%20as%20%3Fid%20)%0D%0A%20%20%3Fdocid%20rdfs%3Alabel%20%3Ft%20.%0D%0A%7D&format=JSON&limit=25&offset=0&inference=false`;
        },
        "ajax_conf": {"type": "GET", "dataType": "json"},
        "views": function (kw, c) {
            // url
            var l = c["id"]["value"];
            // コンテンツのタイトル
            var n = c["t"]["value"];
            return `<div class="hc-lines"><a href=${l}>  ${n} </a></div>`
        },
        "max_lines": 5
    },
    {
        "dbname": "fa_fmr",
        "request_type": "sparql",
        "title": function () {
            return "<h3>このキーワードを含むその他のエントリー</h3>"
        },
        "get_url": function (kw) {
            return `http://navi.first.lifesciencedb.jp/fanavi/servlet/query?query=PREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX%20owl%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E%0D%0APREFIX%20ao%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fao%2F%3E%0D%0APREFIX%20aos%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fao%2Fselectors%2F%3E%0D%0APREFIX%20bibo%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fontology%2Fbibo%2F%3E%0D%0APREFIX%20doco%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fspar%2Fdoco%2F%3E%0D%0APREFIX%20dcterms%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX%20foaf%3A%20%3Chttp%3A%2F%2Fxmlns.com%2Ffoaf%2F0.1%2F%3E%0D%0APREFIX%20pav%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fpav%2F%3E%0D%0APREFIX%20nlp%3A%20%3Chttp%3A%2F%2Fnavi.first.lifesciencedb.jp%2Fnlp%2F%3E%0D%0A%0D%0Aselect%20distinct%20(strbefore(substr(str(%3Fs)%2C40)%2C%22%23%22)%20AS%20%3Fid)%20%3Fo%20%3Ft%20%7B%0D%0A%20%20%3Fs%20nlp%3Ayogen%20nlp%3A誘導%20%3B%0D%0A%20%20%20%20%20%3Fp%20%5Brdfs%3Alabel%20%3Fo%5D%20%3B%0D%0A%20%20%20%20%20dcterms%3AisPartOf%7B3%7D%20%2F%20rdfs%3Alabel%20%3Ft%20.%0D%0A%20%20%3Fp%20a%20nlp%3AJoshi%20.%0D%0A%20%20FILTER(lang(%3Fo)%20%3D%20%22ja%22%20%26%26%20contains(%3Fo%2C%20%22${kw}%22))%0D%0A%7D&format=JSON&limit=25&offset=0&inference=false`;
        },
        "ajax_conf": {"type": "GET", "dataType": "json"},
        "views": function (kw, c) {
            // url
            var l = c["id"]["value"];
            // コンテンツのタイトル
            var n = c["t"]["value"];
            return `<div class="hc-lines"><a href=${l}>  ${n} </a></div>`
        },
        "max_lines": 5
    }
];
