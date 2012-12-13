<div id="accordion" class="hubby-meeting">
<div class="hubby-meeting-header">
  <p>Department: ${meeting.dept.name}.</p>
  <p>Meeting for ${meeting.date.strftime("%A, %B %d, %Y")}.</p>
</div>
<div class="hubby-meeting-list">
<% section = "start" %>
%for mitem in meeting.meeting_items:
    %if mitem.type != section and mitem.type is not None:
        <% section = mitem.type %>
	<h3 class="hubby-meeting-agenda-header">${mitem.type.capitalize()} Agenda</h3>
     %endif
	<div class="hubby-meeting-item">
	  <div>${mitem.item.name}</div>
	  <p class="hubby-meeting-item-status">Status:  ${mitem.item.status}</p>
	  <p class="hubby-meeting-item-text">${mitem.item.title}</p>
      <!--
      <ul class="hubby-meeting-item-attachments">
	%for att in mitem.item.attachments:
	    <li>${att.name}</li>
	%endfor
      </ul>
      -->
	</div>
%endfor
</div>
</div>
