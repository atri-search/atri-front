$(document).ready(function() {
    var rdeditor = ace.edit("readonly-editor", {
       wrap:1
    });
    var JsonMode = ace.require("ace/mode/json").Mode;
    rdeditor.session.setMode(new JsonMode());
    rdeditor.renderer.setShowGutter(false);
    rdeditor.setShowPrintMargin(false);
    rdeditor.setHighlightActiveLine(false);
    rdeditor.setReadOnly(true);
    rdeditor.setOptions({
        fontFamily: "IBM Plex Mono",
    });
});
