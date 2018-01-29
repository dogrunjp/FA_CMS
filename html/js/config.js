var parser = {
    "dbpedia": function (d) {
        return [d.slice(d)]
    },
    "sparql": function (d) {
        return d["results"]["bindings"];
    }
};

var cards = [
    {
        "dbname": "dbpedia",
        "request_type": "dbpedia",
        "title": function (kw) {
            var base_url = "http://ja.dbpedia.org/page/";
            return `<h3>DBpedia japanese: <a href=${base_url}${kw}>${kw}</a></h3>`
        },
        "get_url": function (kw) {
            return `http://ja.dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fja.dbpedia.org&query=select+distinct+*+where+%7B+%3Chttp%3A%2F%2Fja.dbpedia.org%2Fresource%2F${kw}%3E+dbpedia-owl%3Aabstract+%3Fo+.++%7D+LIMIT+1&should-sponge=&format=text%2Fcsv&timeout=0&debug=on`
        },
        "ajax_conf": {"type": "GET", "dataType": "text"},
        "views": function (kw, c) {
            var elem = c.slice(3);
            return  `<p>${elem}</p>`
        },
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
            var l = c["id"]["value"] + ".html"
            var n = c["t"]["value"]
            return `<div class="hc-lines"><a href=${l}><i class="fas fa-link"></i>  ${n} </a></div>`
        },
        "max_lines": 5
    }
];





