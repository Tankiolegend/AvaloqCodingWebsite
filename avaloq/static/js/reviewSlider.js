let question1 = true;

function changeQuestion1() {
    question1 = true;
    console.info("quesiton1 = ", question1);
    slider.max = code_entry0.length - 1;
    updateEditor();
    hideResultBox(2);
}

function changeQuestion2() {
    question1 = false;
    console.info("quesiton1 = ", question1, "i.e. showing Q2");
    slider.max = code_entry1.length - 1;
    console.info(slider);
    updateEditor();
}


function showVerdicts() {
    var total = [0, 0];
    const compiler = "#compiler";
    const test_input = "#test_input";
    const user_output = "#user_output";

    cloneResultBox();
    hideResultBox(2);
    for (i = 0; i < 2; i++) { //2 questions
        var v = verdicts[i];
        if (verdicts[i].length === 1) { //compilation error
            var rb = document.getElementById('resultBox1'); //no of result box
            document.getElementById("v-pills-home-tab" + (i + 1).toString() + '0').innerHTML = "Test Case <img src = \"/static/images/cross.png\" >";
            document.getElementById("v-pills-home-tab" + (i + 1).toString() + '0').style.color = "red";
            $(compiler + ((i + 1) * 10).toString()).text(v[i].compiler);
            $(user_output + ((i + 1) * 10).toString()).text(v[i].user_output);
        } else {
            const count = v.length; //number of test cases
            makeCopies(count, (i + 1), v);

            for (j = 0; j < v.length; j++) {
                if (j === 0) {
                    if ((v[j].compiler.localeCompare('Compilation Successful')) === 0) {

                        document.getElementById("v-pills-home-tab" + (i + 1).toString() + j.toString()).innerHTML = "Test Case <img src = \"/static/images/tick.png\" >";
                        document.getElementById("v-pills-home-tab" + (i + 1).toString() + j.toString()).style.color = "#1ecc1e";

                    } else {

                        document.getElementById("v-pills-home-tab" + (i + 1).toString() + j.toString()).innerHTML = "Test Case <img src = \"/static/images/cross.png\" >";
                        document.getElementById("v-pills-home-tab" + (i + 1).toString() + j.toString()).style.color = "red";

                    }
                } else {
                    if ((v[j].compiler.localeCompare('Compilation Successful')) === 0) {

                        document.getElementById("v-pills-profile-tab" + (i + 1).toString() + j.toString()).innerHTML = "Test Case <img src = \"/static/images/tick.png\" >";
                        document.getElementById("v-pills-profile-tab" + (i + 1).toString() + j.toString()).style.color = "#1ecc1e";

                    } else {

                        document.getElementById("v-pills-profile-tab" + (i + 1).toString() + j.toString()).innerHTML = "Test Case <img src = \"/static/images/cross.png\" >";
                        document.getElementById("v-pills-profile-tab" + (i + 1).toString() + j.toString()).style.color = "red";

                    }
                }
                $(compiler + (i + 1).toString() + j.toString()).text(v[j].compiler);
                $(test_input + (i + 1).toString() + j.toString()).text(v[j].test_case);
                $(user_output + (i + 1).toString() + j.toString()).text(v[j].user_output);
            }
        }
    }
}

function cloneResultBox() {
    const resultBoxCopy = multiplyNode(document.querySelector('#resultBox1'), true);
    resultBoxCopy.id = "resultBox2";
    // change ids of cloned div
    document.querySelector("#resultBox2 > #myrow > #mycol > #v-pills-tab > #v-pills-home-tab10").id = 'v-pills-home-tab20';
    //change id for right box
    document.querySelector("#resultBox2 > #myrow > #rightBox > #v-pills-tabContent > #tc-10").id = 'tc-20';
    document.querySelector("#resultBox2 > #myrow > #rightBox > #v-pills-tabContent > #tc-20 > #boxes > #compiler10").id = 'compiler20';
    document.querySelector("#resultBox2 > #myrow > #rightBox > #v-pills-tabContent > #tc-20 > #input > #boxes > #test_input10").id = 'test_input20';
    document.querySelector("#resultBox2 > #myrow > #rightBox > #v-pills-tabContent > #tc-20 > #boxes > #user_output10").id = 'user_output20';
    //update link
    document.querySelector("#resultBox2 > #myrow > #mycol > #v-pills-tab > #v-pills-home-tab20").href = "#tc-20";
}

function makeCopies(count, box_id, v) {
    for (c = 1; c < count; c++) {
        const tc_no = count - c;

        // clone divs
        const copyDiv = multiplyNode(document.querySelector('#tc-' + (box_id * 10).toString()), true);
        copyDiv.id = "tc-" + box_id.toString() + tc_no.toString();
        copyDiv.setAttribute('aria-labelledby', "v-pills-profile");
        copyDiv.classList.remove("show", "active");

        copyDiv.querySelector("#compiler" + (box_id * 10).toString()).id = "compiler" + box_id.toString() + tc_no.toString();
        copyDiv.querySelector("#test_input" + (box_id * 10).toString()).id = "test_input" + box_id.toString() + tc_no.toString();
        copyDiv.querySelector("#user_output" + (box_id * 10).toString()).id = "user_output" + box_id.toString() + tc_no.toString();
        //set values:

        // clone links to divs
        const copy = multiplyNode(document.querySelector('#v-pills-home-tab' + (box_id * 10).toString()), true);
        copy.href = "#tc-" + box_id.toString() + tc_no.toString();
        copy.id = "v-pills-profile-tab" + box_id.toString() + tc_no.toString();
        // copy.classList.remove("show");
        copy.classList.remove("active");
        copy.setAttribute('aria-controls', "v-pills-profile");
        copy.setAttribute('aria-selected', "false");
        copy.innerHTML = "Test Case " + tc_no.toString();
    }
}

function multiplyNode(node, deep) {
    var copy = node.cloneNode(deep);
    node.parentNode.insertBefore(copy, node.nextSibling);
    return copy;
}

function hideResultBox(id) {
    if (id === 1) {
        document.getElementById("resultBox1").style.display = 'none';
        document.getElementById("resultBox2").style.display = 'block';
    } else {
        document.getElementById("resultBox2").style.display = 'none';
        document.getElementById("resultBox1").style.display = 'block';
    }
}

function updateEditor() {
    if (question1) {
        if (slider.value > code_entry0.length) {
            slider.max = code_entry0.length - 1;
            slider.value = code_entry0.length - 1;
            editor.setValue(code_entry0[slider.value].code);
        } else {
            editor.setValue(code_entry0[slider.value].code);
        }

    } else {
        if (slider.value > code_entry1.length) {
            slider.max = code_entry1.length - 1;
            slider.value = code_entry1.length - 1;
            editor.setValue(code_entry1[slider.value].code);
        } else {
            editor.setValue(code_entry1[slider.value].code);
        }
    }
}