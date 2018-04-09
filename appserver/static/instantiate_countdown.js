require(["jquery", 
         "splunkjs/ready!", 
         "splunkjs/mvc/simplexml/ready!", 
         "splunkjs/mvc", 
         "/static/app/SA-ctf_scoreboard_admin/jquery.countdown.js", 
         "/static/app/SA-ctf_scoreboard_admin/jquery.ui.timepicker.js" ], function($, mvc){

  $('#timepicker').timepicker( {
  	showPeriod: true,
    showLeadingZero: true
    } );

  $('#timepicker').on("change", function () {
    var rightnow = new Date();
    var endDateTime = $('#timepicker').timepicker('getTimeAsDate')
    endDateTime.setFullYear(rightnow.getFullYear())
    endDateTime.setMonth(rightnow.getMonth())
    endDateTime.setDate(rightnow.getDate())

    $('#clock').countdown(endDateTime, function(event) {
      $(this).html(event.strftime('%H:%M:%S'));
    });
  });

  $("#settings").on("click", function () {
        $("#showtimepickerdiv, #hidetimepickerdiv").toggle();
    });
});







