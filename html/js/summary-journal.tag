<summary>
    <div id="contentleft_main">
        <h2>{opts.search}の検索結果 {opts.found}</h2>
        <div id="loader">
            <img src="./images/loading.gif" style="display: block;" align="center">
        </div>
        <div class="autopagerize_page_element">

            <virtual each="{list}">
                <div class="article">

                    <h1><a href={URL} rel="bookmark" id={URL} ></a></h1>
                    <div class="article_thumb">
                        <p class="date">{pub_date}</p>
                        <p><strong>{author}</strong><br>
                            DOI: <a href=https://doi.org/{doi}>{doi}</a></p>
                        <p><a href={URL} class="more-link">続きを読む</a></p>
                        <div style="clear:both;">
                        </div>
                    </div>
                </div>
            </virtual>

        </div>

    </div>
    <script>
        var self = this;
        var v = encodeURIComponent(opts.search);

        $.getJSON('https://script.google.com/macros/s/AKfycbxRUrpftHbs62tP7PFas6Kvd6quoNw_CazWSlTOAOV76fW8f05Z/exec?fa=true&j='+ v,
            function(data){
                var loader = document.getElementById("loader")
                loader.style.display = "none";
                // this.listにページのデータをbind
                this.list = data;
                opts.found = this.list.length + "件";
                this.update();
                // タグがエスケープされないようにh2>aのinnerHTMLを利用する
                for (var i in self.list){
                    var elm = document.getElementById(data[i]["URL"]);
                    elm.innerHTML = data[i]["title"]
                }
            }.bind(this));

    </script>

</summary>