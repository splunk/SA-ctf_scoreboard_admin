require([
    'underscore',
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/tableview',
    "splunkjs/mvc/searchmanager",
    'splunkjs/mvc/simplexml/ready!'
], function(_, $, mvc, TableView, SearchManager) {
    var current_sm = new SearchManager({
        id: "current_sm",
        preview: true,
        search: mvc.tokenSafe('| inputlookup ctf_badges \
                 | lookup ctf_badge_entitlements BadgeNumber \
                 | search `get_user_info` \
                 | stats dc(Team) as "Team Count" values(Team) as Teams \
                         dc(DisplayUsername) as "User Count" \
                         values(DisplayUsername) as Users \
                    by BadgeNumber BadgeURL BadgeName BadgeDescription \
                 | sort BadgeNumber \
                 | rename BadgeNumber as "Num" \
                 | search Num="$ebadge$" \
                 | rename "Teams" as "Teams Represented"')
    }, {tokens: true});

    var assign_sm = new SearchManager({
        id: "assign_sm",
        preview: false,
        autostart: false,
        search: mvc.tokenSafe('| makeresults \
                               | sendalert award_ebadge \
                                 param.recipient="$recipient$" \
                                 param.ebadge="$ebadge$" \
                                 param.notes="$notes$" \
                                 param.award_to_entire_team="$award_to_entire_team$"'),
    }, {tokens: true});

    var badge_table = new TableView({
        id: "badge_table",
        managerid: "current_sm",
        el: $("#badge_div")
    }).render();

    var defaultTokenModel = mvc.Components.get("default");

    var CustomTableImageRenderer = TableView.BaseCellRenderer.extend({
        canRender: function(cell) {
            return cell.field === 'BadgeURL' || cell.field === 'Team' || cell.field === 'BadgeName' || cell.field === 'Unique Count';
        },
        render: function($td, cell) {
            if (cell.field === 'BadgeURL') {
                badge_list = cell.value.split(",");
                prepared_html = '<div class="badge-image-row">';
                badge_list.forEach(function(badge){
                    prepared_html += '<img class="badge-image" src="' + badge.trim() + '" />';
                }); 
                prepared_html += '</div>';
                $td.html(prepared_html);
            }
            if (cell.field === 'Team' || cell.field === 'Unique Count' || cell.field === 'BadgeName' ) {
                prepared_html = '<div class="team-text">' + cell.value + '</div>';
                $td.html(prepared_html);
            }
        }
    });
    badge_table.addCellRenderer(new CustomTableImageRenderer());

    var diybtn = document.getElementById("diy_submit");
    diybtn.addEventListener("click", 
        function(){ 
            assign_sm.startSearch();
            assign_sm.on('search:done', function() {
                current_sm.startSearch();
            }); 
        }
    );

});