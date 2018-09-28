<summary>
    <div id="contentleft_main">
        <h2>{opts.search}の検索結果 {opts.found}</h2>
        <div class="autopagerize_page_element">

            <virtual each="{list}">
                <div class="article">

                    <h1><a href={URL} rel="bookmark" id={URL} ></a></h1>
                    <div class="article_thumb">
                        <p class="date">{pub_date}</p>
                        <p><strong>{author}</strong><br>
                            DOI: <a href=http://doi.org/{doi}>{doi}</a></p>
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
        var v = opts.search;

        $.getJSON('https://script.google.com/macros/s/AKfycbxRUrpftHbs62tP7PFas6Kvd6quoNw_CazWSlTOAOV76fW8f05Z/exec?fa=true&j='+ v,
            function(data){
                this.list = data;
                opts.found = this.list.length + "件";
                this.update();
                for (item of self.list){
                    var elm = document.getElementById(item["URL"])
                    elm.innerHTML = item["title"]
                }
            }.bind(this));

    </script>

</summary>