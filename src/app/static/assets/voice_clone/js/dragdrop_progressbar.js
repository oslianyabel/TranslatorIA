class FileUpload {
    constructor(input) {
        this.input = input
        this.max_length = 1024 * 1024 * 10; // 10 mb
    }

    upload() {
        this.create_progress_bar();
        this.initFileUpload();
    }

    initFileUpload() {
        this.file = this.input.files[0];
        this.upload_file(0, null);
    }
    create_progress_bar() {
        var progress = `<div class="file-details">
                            <p class="filename"></p>
                            <div class="progress" style="margin-top: 5px;">
                                <div class="progress-bar bg-success" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%">
                                </div>
                            </div>
                        </div>`
        document.getElementById('uploaded_files').innerHTML = progress
    }
    upload_file(start, path) {
        var end; // whether an upload is ended or not.
        var self = this;
        var existingPath = path;  // null if file can be uploaded as a whole or contains the path at which the previous chunk was uploaded
        var formData = new FormData(); // an object to hold the data that will be sent to server.
        var nextChunk = start + this.max_length + 1; // start of next part of file if exists
        var currentChunk = this.file.slice(start, nextChunk); // current part of file
        var uploadedChunk = start + currentChunk.size // sizeof aggregation of all chunks uploaded so far
        
        if (uploadedChunk >= this.file.size) {
            end = 1;
        } else {
            end = 0;
        }

        formData.append('file', currentChunk)
        formData.append('filename', this.file.name)
        formData.append('end', end)
        formData.append('existingPath', existingPath);
        formData.append('nextSlice', nextChunk);
        $('.filename').text(this.file.name)
        //$('.textbox').text(" ... ")
        $.ajaxSetup({
            headers: { // make sure to send the header
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        });
        $.ajax({
            xhr: function () { // to compute the amount of file that has been uploaded
                var xhr = new XMLHttpRequest();
                xhr.upload.addEventListener('progress', function (e) {
                    if (e.lengthComputable) {
                        if (self.file.size < self.max_length) {
                            var percent = Math.round((e.loaded / e.total) * 100);
                        } else {
                            var percent = Math.round((uploadedChunk / self.file.size) * 100);
                        }
                        $('.progress-bar').css('width', percent + '%')
                        $('.progress-bar').text(percent + '%')
                    }
                });
                return xhr;
            },

            url: '/projects/', // the url at which the request will be made
            type: 'POST', // request method
            dataType: 'json', // the type in which we pass the data
            cache: false,
            processData: false,
            contentType: false,
            data: formData, // actual data that will be passed
            error: function (xhr) { // called when error occurs while doing some action
                // alert(xhr.statusText);
            },
            success: function (res) { // called when action is successfully completed
                if (nextChunk < self.file.size) {
                    // upload file in chunks
                    existingPath = res.existingPath
                    self.upload_file(nextChunk, existingPath);
                } else {
                    // upload complete
                    $('.textbox').text(res.data);
                    // alert(res.data)
                }
            }
        });
    };
}

(function ($) {
    $('#upload_video_btn_id').on('click', (event) => {
        event.preventDefault();
        let fileInput = document.querySelector('#id_file');  
        var uploader = new FileUpload(fileInput);
        uploader.upload();
    });
})(jQuery);


ondragenter = function(evt) {
    evt.preventDefault();
    evt.stopPropagation();
};
ondragover = function(evt) {
    evt.preventDefault();
    evt.stopPropagation();
};
ondragleave = function(evt) {
    evt.preventDefault();
    evt.stopPropagation();
};  
ondrop = function(evt) {
    evt.preventDefault();
    evt.stopPropagation();
    var fileInput = document.querySelector('#id_file');
    fileInput.files = evt.originalEvent.dataTransfer.files;
    // console.log(fileInput);
   
    // var uploader = new FileUpload(fileInput);
    // uploader.upload();
};
$('#dropBox')
    .on('dragover', ondragover)
    .on('dragenter', ondragenter)
    .on('dragleave', ondragleave)
    .on('drop', ondrop);
