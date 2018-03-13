function tankuang(pWidth,content) {
    $("#msg").remove();
    var html = '<div id="msg" style="position:fixed;top:50%;width:100%;height:30px;line-height:30px;margin-top:-15px;"><p style="background:#000;opacity:0.8;width:' + pWidth + 'px;color:#fff;text-align:center;padding:10px 10px;margin:0 auto;font-size:12px;border-radius:4px;">' + content + '</p></div>'
    $("body").append(html);
    var t = setTimeout(next, 2000);

    function next() {
        $("#msg").remove();

    }
}

$('.navbar-avatar').parent().parent().hover(function () {
    $('ul.dropdown-menu').toggle();}
)

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





