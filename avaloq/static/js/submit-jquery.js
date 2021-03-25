function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});



//TIME GLOBAL VARIABLES
var time = new Date(Date.now()); //time now
var temp_time = time; // to compare if certain time passed
temp_time.setSeconds(time.getSeconds() + 5); // set temp_time to be +10 seconds
var new_time; //helper variable


function updateEditor() {
    let info;

    if ($("#language").val() === "java") {

        info = CodeMirror.findModeByMIME(modeJava);
        editor.setOption("mode", modeJava);
        CodeMirror.autoLoadMode(editor, info.mode);
        editor.setValue(java_code);
    } else if ($("#language").val() === "javascript") {

        info = CodeMirror.findModeByMIME(modeJS);
        editor.setOption("mode", modeJS);
        CodeMirror.autoLoadMode(editor, info.mode);
        editor.setValue(js_code);
    } else {

        info = CodeMirror.findModeByMIME(modePython);
        editor.setOption("mode", modePython);
        CodeMirror.autoLoadMode(editor, info.mode);
        editor.setValue(python_code);
    }
}
var time_Expires = null; //new Date();
$.ajax({
    type: 'GET',
    success: function(response) {
        if (response.redirect === true) {

            window.location.href = response.redirect_url;

        } else {

            time_Expires = new Date(response.exp_time);

        }
    },
    error: function() {
        time_Expires = new Date(Date.now() + 45 * 60000);
    }
});

var alert_ind = false;
// Update the count down every 1 second

var x = setInterval(function() {
    if (time_Expires !== null) {
        // Get today's date and time
        var now = new Date().getTime();

        // Find the distance between now and the count down date
        var distance = time_Expires - now;

        // Time calculations for hours, minutes and seconds
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Display the result in the element with id="demo"
        try {
            document.getElementById("timer").innerHTML = hours + "h " + minutes + "m " + seconds + "s ";
        } catch (e) {

        }
        // document.getElementById("timer").innerHTML = hours + "h " + minutes + "m " + seconds + "s ";
        // If the count down is finished, write some text
        if (distance < 0) {
            clearInterval(x);
            try {
                document.getElementById("timer").innerHTML = "Time Expired";
            } catch (e) {

            }
            if (alert_ind == false) {

                // alert('Time expired, you\'re code will now be submitted');
                alert_ind = true;
            }
            document.getElementById("submit").click();
        }
    }
}, 1000);



$(document).ready(function() {


    // give the initial language setup
    if ($("#language").val() === "java") {
        if (editor.getValue() === "") {
            editor.setValue(java_code);
        } else {}
    } else if ($("#language").val() === "javascript") {
        if (editor.getValue() === "") {
            editor.setValue(js_code);
        } else {}
    } else {
        if (editor.getValue() === "") {
            editor.setValue(python_code);
        } else {}
    }

    $("#code_form").keypress(function() {

        //put codemirror back to form again
        document.getElementById("code_text").value = editor.getValue();

        //remember last status of the editor for recovery
        if ($("#language").val() === "java") {
            java_code = $("#code_text").val();
        } else if ($("#language").val() === "javascript") {
            js_code = $("#code_text").val();
        } else {
            python_code = $("#code_text").val();
        }



        new_time = new Date(Date.now());
        if (new_time.getTime() > temp_time.getTime()) {
            time = new_time;
            temp_time.setSeconds(time.getSeconds() + 5);


            var code = $("#code_text").val();
            var lang = $("#language").val();

            $.ajax({
                type: 'POST',
                data: { 'code': code, 'language': lang, 'save_to_db': true, },

                // handle a successful response
                success: function(response) {


                    if (response.redirect === true) {

                        window.location.href = response.redirect_url;

                    }
                },

                // handle a non-successful response
                error: function() {

                    console.info("failure");
                }
            });
        }
    });
    //    run code ajax
    $("#run").click(function() {

        const code = editor.getValue();
        const lang = $("#language").val();
        const test_input = $("#test_input").val();
        var checkBox = document.getElementById("user_test_input");
        const cust_input = checkBox.checked;
        $.ajax({
            type: 'POST',
            data: {
                'code_text': code,
                'language': lang,
                'user_test_input': cust_input,
                'test_input': test_input,
            },

            // if success, then disply results in testbox
            success: function(response) {

                const compiler = "#compiler";
                const test_input = "#test_input";
                const user_output = "#user_output";

                var n = Number(response.no_tests);

                if (response.redirect === true) {

                    window.location(response.redirect_url);

                } else {

                    for (i = 0; i < n; i++) {
                        if (response.test_input === null) {
                            // compilation error
                            $(compiler + i.toString()).text(response.compiler);
                            $(user_output + i.toString()).text(response.user_output);
                            hideTestCaseName();
                            selectTC0(response.compiler);
                        } else {
                            $(compiler + i.toString()).text(response.compiler[i]);
                            $(test_input + i.toString()).text(response.test_input[i]);
                            $(user_output + i.toString()).text(response.user_output[i]);

                            if (cust_input) { //custom test case
                                hideTestCaseName();
                                selectTC0(response.compiler);
                            } else { //sample test cases
                                showTestCaseName(response.compiler);
                                if (toCopy) { makeCopies(n); }
                            }
                        }

                    }
                }
            },

            // handle a non-successful response
            error: function() {
                console.info("failure");
            }
        });
    });

});

var toCopy = true;
var totalTestCases = 1;

function selectTC0(compiler_response) {

    if ((compiler_response[0].localeCompare('Compilation Successful')) === 0) {

        document.getElementById("v-pills-home-tab").innerHTML = "Test Case <img src = \"/static/images/tick.png\" >";
        document.getElementById("v-pills-home-tab").style.color = "#1ecc1e";

    } else {

        document.getElementById("v-pills-home-tab").innerHTML = "Test Case <img src = \"/static/images/cross.png\" >";
        document.getElementById("v-pills-home-tab").style.color = "red";

    }
    document.getElementById('v-pills-home-tab').classList.add("active");
    document.getElementById('tc-0').classList.add("active", "show");

    for (j = 1; j < totalTestCases; j++) {
        document.getElementById("v-pills-profile-tab" + j.toString()).classList.remove("active");
        document.getElementById("tc-" + j.toString()).classList.remove("active", "show");
    };

}

function makeCopies(count) {
    totalTestCases = count;
    for (c = 1; c < count; c++) {
        const tc_no = count - c;

        // clone divs
        const copyDiv = multiplyNode(document.querySelector('#tc-0'), true);
        copyDiv.id = "tc-" + tc_no.toString();
        copyDiv.setAttribute('aria-labelledby', "v-pills-profile");
        copyDiv.classList.remove("show", "active");

        copyDiv.querySelector("#compiler0").id = "compiler" + tc_no.toString();
        copyDiv.querySelector("#test_input0").id = "test_input" + tc_no.toString();
        copyDiv.querySelector("#user_output0").id = "user_output" + tc_no.toString();


        // clone links to divs
        const copy = multiplyNode(document.querySelector('#v-pills-home-tab'), true);
        copy.href = "#tc-" + tc_no.toString();
        copy.id = "v-pills-profile-tab" + tc_no.toString();
        copy.classList.remove("active");
        copy.setAttribute('aria-controls', "v-pills-profile");
        copy.setAttribute('aria-selected', "false");
        copy.innerHTML = "Test Case " + tc_no.toString() + " <img src = \"/static/images/tick.png\" >";


    }
    toCopy = false;

}

function multiplyNode(node, deep) {
    copy = node.cloneNode(deep);
    node.parentNode.insertBefore(copy, node.nextSibling);
    return copy;
}

// show/ hide test case name when compilation error appears
function hideTestCaseName() {

    for (c = 1; c < totalTestCases; c++) {
        var id = "v-pills-profile-tab" + c.toString();
        document.getElementById(id).style.display = "none";
    }
}

function showTestCaseName(compiler_responses) {

    if ((compiler_responses[0].localeCompare('Compilation Successful')) === 0) {

        document.getElementById("v-pills-home-tab").innerHTML = "Test Case 0 <img src = \"/static/images/tick.png\" >";
        document.getElementById("v-pills-home-tab").style.color = "#1ecc1e";

    } else {

        document.getElementById("v-pills-home-tab").innerHTML = "Test Case 0 <img src = \"/static/images/cross.png\" >";
        document.getElementById("v-pills-home-tab").style.color = "#ff0000";
    }


    for (c = 1; c < totalTestCases; c++) {
        var id = "v-pills-profile-tab" + c.toString();
        document.getElementById(id).style.display = "block";
        if ((compiler_responses[c].localeCompare('Compilation Successful')) === 0) {
            document.getElementById(id).innerHTML = "Test Case" + c.toString() + " <img src = \"/static/images/tick.png\" >";
            document.getElementById(id).style.color = "#1ecc1e";

        } else {

            document.getElementById(id).innerHTML = "Test Case " + c.toString() + "<img src = \"/static/images/cross.png\" >";
            document.getElementById(id).style.color = "#ff0000";

        }
    }
}



//-----------------------------------------------------------------------------------------------------


//
$(document).ready(function() {
    //     //Disable full page
    $('body').on('cut copy paste', function(e) {
        alert('Cut, copy and paste is not allowed for this exercise.');
        e.preventDefault();
    });

    //      //Disable mouse right click
    $("body").on("contextmenu", function(e) {
        alert('Right click menu is not allowed for this exercise.');
        return false;
    });

    //
    // 	//Fix for ctrl+v still working
    var map = {};
    onkeydown = onkeyup = function(e) {
        e = e || event; // to deal with IE
        map[e.keyCode] = e.type == 'keydown';
        if (map[17] && map[86]) {
            alert('Cut, copy and paste is not allowed for this exercise.');
            event.preventDefault();
            map[86] = false;
        }else if (map[123]){
			alert('Inspect element is not allowed!');
            event.preventDefault();
			map[123] = false;
			
		};
    };


});