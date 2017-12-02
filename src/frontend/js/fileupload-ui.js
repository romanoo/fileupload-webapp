"use strict";

function refresh() {
    $.get("/files", function (response) {
        var template = $('#render_files_tpl').html();
        Mustache.parse(template);
        var rendered = Mustache.render(template, {
            "files" : response.Files
        });
        $("#tableapp").find("tbody").html(rendered);
        $("#tableapp").find(".close").each(function(i, elt){
            var name = $(elt).attr("name");
            if(name !== undefined){
                $(elt).click(function(){
                    $.ajax({
                        url: "/files/" + name,
                        type: "DELETE",
                        success: function() {
                            refresh();
                        }
                    });
                });
            }
        });
    });
}

function init() {
    refresh();

    $("#fileupload").fileupload({
        formData: {},
        maxChunkSize: 1000000,
        url: "/files",
        start: function (e, data) {
            $("#progress .progress-bar").css("width", "0%");
            $("#progress .progress-bar").html("0%");
            $(":button").prop("disabled", true);
        },
        done: function (e, data) {
            console.log("done");
            refresh();
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $("#progress .progress-bar").css("width", progress + "%");
            $("#progress .progress-bar").html(progress + "%");
        }
    }).prop("disabled", !$.support.fileInput).parent().addClass($.support.fileInput ? undefined : "disabled");

    $("#fileupload").bind("fileuploadsubmit", function (e, data) {
        data.formData = { "fileuploadsubmit": parseInt(data._progress.loaded, 10).toString() };
    });
}