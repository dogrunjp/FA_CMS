var parser = {
    "dbpedia": function (d) {
        return [d.slice(d)]
    },
    "sparql": function (d) {
        return d["results"]["bindings"];
    },
    "link": ["link"]

};

var cards = [
    {
        "dbname": "refex",
        "request_type": "dbpedia",
        "title": function (kw) {
            var base_url = "https://refex.dbcls.jp/genelist.php?gene_name%5B%5D=";
            return `<h3>RefEx: <a href=${base_url}${kw}>${kw}</a></h3>`
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
        "request_type": "dbpedia",
        "title": function (kw) {
            var base_url = "https://ggrna.dbcls.jp/ja/";
            return `<h3>ggrna: <a href=${base_url}${kw}>${kw}</a></h3>`
        },
        "get_url":function () {
            return []
        },
        "ajax_conf": {"type": "GET", "dataType": "text"},
        "views": "",
        "max_lines": 5
    },
    {
        "dbname": "fa",
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





