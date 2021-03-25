$(function() {
    $("input[type='checkBox']").change(function() {
        var len = $("input[type='checkBox']:checked").length;
        if (len != 2)
            $("input[type='submit']").prop("disabled", true);
        else
            $("input[type='submit']").removeAttr("disabled");
    });
    $("input[type='checkBox']").trigger('change');

});