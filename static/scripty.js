$(document).on('click', '#close-preview', function() {
    $('.image-preview').popover('hide');
    // Hover befor close the preview
    $('.image-preview').hover(
        function () {
           $('.image-preview').popover('show');
        },
         function () {
           $('.image-preview').popover('hide');
        }
    );
});

$(function() {
    // Create the close button
    var closebtn = $('<button/>', {
        type:"button",
        text: 'x',
        id: 'close-preview',
        style: 'font-size: initial;',
    });
    closebtn.attr("class","close pull-right");
    // Set the popover default content
    $('.image-preview').popover({
        trigger:'manual',
        html:true,
        title: "<strong>Preview</strong>"+$(closebtn)[0].outerHTML,
        content: "There's no image",
        placement:'bottom'
    });
    // Clear event
    $('.image-preview-clear').click(function(){
        $('.image-preview').attr("data-content","").popover('hide');
        $('.image-preview-filename').val("");
        $('.image-preview-clear').hide();
        $('.image-preview-input input:file').val("");
        $(".image-preview-input-title").text("Browse");
    });
    // Create the preview image
    $(".image-preview-input input:file").change(function () {
        var img = $('<img/>', {
            id: 'dynamic',
            width:250,
            height:200
        });
        var file = this.files[0];
        var reader = new FileReader();
        // Set preview image into the popover data-content
        reader.onload = function (e) {
            $(".image-preview-input-title").text("Change");
            $(".image-preview-clear").show();
            $(".image-preview-filename").val(file.name);
            img.attr('src', e.target.result);
            $(".image-preview").attr("data-content",$(img)[0].outerHTML).popover("show");
        };
        reader.readAsDataURL(file);
    });

    $("#form").submit(function(e) {
        var formData = new FormData(document.querySelector('#form'));

        $.ajax({
            type: 'POST',
            url: '/process_character_sheet',
            data: formData,
            processData: false,
            contentType: false ,
            success: function(data) {
                var ts = Date.now(), img = new Image;
                var text = data.text.map(function (text) {
                    return("<img height='300' width='300' onerror=\"onError('" + text + "', " + ts + ")\" src='" + text + "'></img>");
                }).join('<br/>');
                $("body").append('<div class="container">\n' +
                    '      <div class="row">\n' +
                    '          <div class="col-sm-2"></div>\n' +
                    '          <div class="col-sm-8">\n' +
                    '  <div class="alert alert-success" role="alert">\n' +
                    '  <h2 class="alert-heading">Generated character images:</h2>\n' +
                    '  <hr>\n' +
                    '  <p class="mb-0">' + text + '</p>\n' +
                    '</div>\n' +
                    '          </div>\n' +
                    '          <div class="col-sm-2"></div>\n' +
                    '      </div>\n' +
                    '  </div>');
            }, error: function(err) {
                console.log(err);
            }
        });
        e.preventDefault();
    });
});

function onError(src, ts) {
    console.log(this);
    if (Date.now() - ts < 10000) {
        setTimeout(function() { this.src = src; }, 1000);
    } else {
        this.style.display = 'none'; 
    }
}