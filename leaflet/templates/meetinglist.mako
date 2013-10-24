<div class="meetinglist-view">
  <% dtformat = '%b %d %Y - %H:%M:%S' %>
  <% timeformat = '%I:%M %p' %>
  <div class="listview-header">
    <p>There are ${len(meetings)} meetings.</p>
  </div>
  <div class="listview-list">
    <% route = 'hubby_main' %>
    <% ctxt = 'viewmeeting' %>
    <% mkurl = request.route_url %>
    %for m in meetings:
    <% url = mkurl(route, context=ctxt, id=m.id) %>
    <div class="listview-list-entry">
      %if not m.time:
      <h4>No Time</h4>
      %endif
      <a href="${url}">${m.title}</a>&nbsp;<a href="${m.link}">(legistar)</a>
    </div>
    %endfor
  </div>
</div>

