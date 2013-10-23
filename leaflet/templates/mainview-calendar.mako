<div id="data-area">
  <% evurl = request.route_url('hubby_json', context='meetingrange', id='events') %>
  <input id="event-source-url" type="hidden" value="${evurl}" />
</div>
<div id="loading">
  <h2>Loading Events</h2>
</div>
<div id="maincalendar">
</div>
