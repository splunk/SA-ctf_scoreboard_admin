require([
    'underscore',
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/searchmanager',
    'splunkjs/mvc/simplexml/ready!',
    'splunkjs/ready!'
], function(_, $, mvc, SearchManager) {
    $('#start_time_picker').datetimepicker({
        dateFormat: "yy-mm-dd",
        timeFormat: "HH:mm z",
        controlType: "select",
        onClose: function() {
            var myDate = $('#start_time_picker').datetimepicker("getDate")
            var myEpoch = myDate.getTime() / 1000
            var myHtml = myEpoch
            mvc.Components.get('submitted').set('StartTimeToken', myEpoch);
        }
    });

    $('#end_time_picker').datetimepicker({
        dateFormat: "yy-mm-dd",
        timeFormat: "HH:mm z",
        controlType: "select",
        onClose: function() {
            var myDate = $('#end_time_picker').datetimepicker("getDate")
            var myEpoch = myDate.getTime() / 1000
            var myHtml = myEpoch
            mvc.Components.get('submitted').set('EndTimeToken', myEpoch);
        }
    });

    var updateTimesSM = new SearchManager({
        id: "updateTimesSM",
        app: "SA-ctf_scoreboard_admin",
        cache: false,
        autostart: false,
        search: "| inputlookup ctf_questions"
    });
    mvc.Components.get('submitted').set('somethingchanged', Date.now().toString());


    document.getElementById('submit_button').onclick = function(){
    	
    	document.getElementById("update_results").innerHTML="Starting search...!";
    	//updateTimesSM.finalize();
    	var searchString =  '| inputlookup ctf_questions | eval StartTime=' 
    	                    + mvc.Components.get('submitted').get('StartTimeToken') 
    	                    + '| eval EndTime='
    	                    + mvc.Components.get('submitted').get('EndTimeToken')
    	                    + '| outputlookup ctf_questions';
        updateTimesSM.settings.set("search", searchString);
    	updateTimesSM.startSearch();
    
        updateTimesSM.on('search:failed', function(properties) {
            // Print the entire properties object
            document.getElementById("update_results").innerHTML="Failed!";
        });
    
        updateTimesSM.on('search:progress', function(properties) {
            // Print just the event count from the search job
            document.getElementById("update_results").innerHTML="In progress with " + properties.content.eventCount + " events...";
        });
    
        updateTimesSM.on('search:done', function(properties) {
            // Print the search job properties
            document.getElementById("update_results").innerHTML="Done! Verify results below.";
            mvc.Components.get('submitted').set('somethingchanged', Date.now().toString());
        });
    }
});