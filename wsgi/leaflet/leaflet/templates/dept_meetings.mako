<div class="hubby-dept-meetinglist">
<div class="hubby-dept-meetinglist-header">
  <p>Department: ${dept.name}.</p>
  <p>Meetings for Department: ${dept.name}.</p>
</div>
<ul>
%for meeting in dept.meetings:
<% href = request.route_url('hubby_context', context='viewmeeting', id=meeting.id) %>
    <li class="hubby-dept-meeting-item"><a href="${href}">${meeting.title}</a></li>
%endfor
</ul>
</div>
