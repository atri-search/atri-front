var content = "";

function load_collection() {
      var collection = $('#collection').val();
      if(collection !== null && $('#collection').val() !== 'Corpus'){

        $.ajax({
            url: '/collection/' + collection + '/defaults',
            type: 'get',
            success: function(response){
                $(".advanced-exhibition").html(response);
                var editor = ace.edit("editor", {
                    wrap:1
                });
                var JsonMode = ace.require("ace/mode/json").Mode;
                editor.session.setMode(new JsonMode());
                content = editor.getValue();
            }
        });

        document.getElementById("cog").disabled = false;
      }
  }

  $(document).ready(function() {
    load_collection();
  });

  $('#collection').change(function() {
      load_collection();
  });

  function updateContent() {
      var editor = ace.edit("editor", {
        wrap:1
    });
    var JsonMode = ace.require("ace/mode/json").Mode;
    editor.session.setMode(new JsonMode());
    content = editor.getValue();
  }

  function saveContent() {
    var collection = $('#collection').val();
    var editor = ace.edit("editor", {
        wrap:1
    });
    var JsonMode = ace.require("ace/mode/json").Mode;
    editor.session.setMode(new JsonMode());
    content = editor.getValue();
    var jsonContent = {"search_defaults": content};
    $.ajax({
            url: '/collection/' + collection + '/defaults',
            type: 'post',
            data: JSON.stringify(jsonContent),
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                  if(data.hasOwnProperty('success')){
                      alert(data['success']);
                  }
            }
    });
  }

$('#search-form').submit(function() {
    document.getElementById("advanced").value =  content;
    return true;
});

$('input').on("input", function(e) {
    $(this).val($(this).val().replace("/", ""));
});

$("#cog").click(function(){
    $("#advancedSearchModal").modal('show');
    var editor = ace.edit("editor", {
        wrap:1
    });
    var JsonMode = ace.require("ace/mode/json").Mode;
    editor.session.setMode(new JsonMode());
    editor.renderer.setShowGutter(false);
    editor.setShowPrintMargin(false);
    editor.setHighlightActiveLine(false);
    editor.setOptions({
        fontFamily: "IBM Plex Mono",
    });
    editor.setValue(editor.getValue().trim());
});