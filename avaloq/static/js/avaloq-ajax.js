$(document).ready(function() {


    $('#delete_btn').click(function() {
        if (confirm("Once a candidate is deleted their submission cannot be recovered. Are you sure?") == true) {


            var candidateID = $(this).attr('data-candidateid');
            $.get('/avaloq/delete_candidate', { 'u_id': candidateID },
                function(data) {
                    location.reload();
                })
        }
    });


});