function tankuang(pWidth,content) {
    $("#msg").remove();
    var html = '<div id="msg" style="position:fixed;top:50%;width:100%;height:30px;line-height:30px;margin-top:-15px;"><p style="background:#000;opacity:0.8;width:' + pWidth + 'px;color:#fff;text-align:center;padding:10px 10px;margin:0 auto;font-size:12px;border-radius:4px;">' + content + '</p></div>'
    $("body").append(html);
    var t = setTimeout(next, 2000);

    function next() {
        $("#msg").remove();

    }
}



$(document).ready(function () {
    if ($('.feedback-message')) {
        $('.feedback-message').delay(2000).fadeOut(0.5);
        //tankuang(300, $('.feedback-info').text());

        /*layer.msg($('.feedback-info').text(), {
                skin: 'feedback-info-dialog'
            });*/
    }
})

$(document).ready(function(){
  $(".nav.navbar-nav li.menu-item").each(function(){
    $this = $(this);
    if($this.children('a').attr('href')==String(window.location.pathname)){
      $this.addClass("active");
    }
  });
});




$('.navbar-avatar').parent().parent().hover(function () {
    $('ul.dropdown-menu').toggle();}
)

function submitSearchQuery() {
    var key = $("#navbar-keyword-search-input").val();
    if(!key){
        //alert('haha');
        $('.navbar-search-div').removeClass('div-active').addClass('div-inactive');
        $('#navbar-keyword-search-input').removeClass('input-active').addClass('input-inactive');
    }else{
        $('body>div.container').load('/search?q=' + key)
        //Turbolinks.visit("/search?q=" + key + "&type=" + $(".xzl-search-input").data("search-type"), { action: "replace" })
    }
}


function checkEnterkeyForSearchInput(e) {
    //e.preventDefault();
    console.log(e);
    if (e.keyCode=='13') {
        submitSearchQuery();
    }
    //$('div.container').load('/search?keyword=')
}

$('.navbar-search-btn').click(function (e) {
    if ($('.navbar-search-div').hasClass('div-inactive')) {
        $('.navbar-search-div').removeClass('div-inactive').addClass('div-active');
        $('#navbar-keyword-search-input').removeClass('input-inactive').addClass('input-active').focus();
    } else {
        if ($('#navbar-keyword-search-input').val() === '') {
            $('.navbar-search-div').removeClass('div-active').addClass('div-inactive');
            $('#navbar-keyword-search-input').removeClass('input-active').addClass('input-inactive');
        } else {
            submitSearchQuery(e);
        }
    }
})


String.prototype.trim = function() {
    var str = this,
    str = str.replace(/^\s\s*/, ''),
    ws = /\s/,
    i = str.length;
    while (ws.test(str.charAt(--i)));
    return str.slice(0, i + 1);
}