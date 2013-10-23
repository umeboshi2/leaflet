<div id="accordion" class="hubby-meeting">
<div class="hubby-meeting-header">
  <p>Department: ${meeting.dept.name}.</p>
  <p>Meeting for ${meeting.date.strftime("%A, %B %d, %Y")}.</p>
  <div class="hubby-meeting-header-agenda">
    %if meeting.agenda_status == 'Final':
        <a href="${util.agenda_url(meeting.id, meeting.guid)}">Agenda</a>
    %else:
	Agenda: ${meeting.agenda_status}
    %endif
  </div>
  <div class="hubby-meeting-header-minutes">
    %if meeting.minutes_status == 'Final':
        <a href="${util.minutes_url(meeting.id, meeting.guid)}">Minutes</a>
    %else:
	Minutes: ${meeting.minutes_status}
    %endif
  </div>
</div>
<div class="hubby-meeting-item-list">
<% section = "start" %>
%for mitem in meeting.meeting_items:
    %if mitem.type != section and mitem.type is not None:
        <% section = mitem.type %>
	<h3 class="hubby-meeting-agenda-header">${mitem.type.capitalize()} Agenda</h3>
     %endif
	<div class="hubby-meeting-item">
	  <div class="hubby-meeting-item-info">
	    <div class="hubby-meeting-item-agenda-num">${mitem.agenda_num}</div>
	    <div class="hubby-meeting-item-fileid">${mitem.item.file_id}</div>
	    <!--<div>${mitem.item.name}</div>-->
	    <div class="hubby-meeting-item-status">${mitem.item.status}</div>
	  </div>
	  <div class="hubby-meeting-item-content">
	    <p class="hubby-meeting-item-text">${mitem.item.title}</p>
	    %if mitem.item.attachments:
	    <div class="hubby-meeting-item-attachment-marker">Attachments</div>
	    <div class="hubby-meeting-item-attachments">
	      <div class="hubby-meeting-item-attachments-header">Attachments</div>
	      %for att in mitem.item.attachments:
	      <div><a href="${att.get_link()}">${att.name}</a></div>
	      %endfor
	    </div>
	    %endif
	    %if mitem.item.actions:
	    <div class="hubby-meeting-item-action-marker" id="${mitem.item.id}" onclick="${request.route_url('hubby_frag', context='itemactions', id=mitem.item.id)}">Actions</div>
	    <div class="hubby-meeting-item-actions"></div>
	    %endif
	  </div>
	</div>
%endfor
</div>
</div>
