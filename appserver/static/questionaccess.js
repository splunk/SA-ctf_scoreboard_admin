require([
    'underscore',
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/searchmanager',
    'splunkjs/mvc/simplexml/ready!',
    'splunkjs/ready!'
], function(_, $, mvc, SearchManager) {

    var toggleAccessSM = new SearchManager({
        id: "toggleAccessSM",
        app: "SA-ctf_scoreboard_admin",
        cache: false,
        autostart: false,
        search: "| toggleqaccess"
    });

    mvc.Components.get('submitted').set('somethingchanged', Date.now().toString());
    console.log (mvc.Components.get('submitted').get('somethingchanged'));

    document.getElementById('togglebutton').onclick = function(){
    	toggleAccessSM.startSearch();
        toggleAccessSM.on('search:done', function(properties) {
            mvc.Components.get('submitted').set('somethingchanged', Date.now().toString());
        });
    }
});