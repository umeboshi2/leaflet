<div id="data-area">
  <% url = request.route_url('consult_calendar', context='add', id='somebody') %>
  <% evurl = request.route_url('consult_caljson', context='view', id='event') %>
  <input id="add-event-url" type="hidden" value="${url}" />
  <input id="event-source-url" type="hidden" value="${evurl}" />
</div>
<div id="newevent"></div>
%if request.matchdict['context'] == 'viewevents':
<div id="loading">
  <h2>Loading Events</h2>
</div>
%endif
<div id="maincalendar">
</div>

<div style="clear:both">
</div>
<div class="action-area">
  <div id="action-button-submit">
    submit
  </div>
  <div id="action-info">
  </div>
</div>
