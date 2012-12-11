<div class="hubby-meeting">
<div class="hubby-meeting-header">
  <p>Department: ${meeting.dept.name}.</p>
  <p>Meeting for ${meeting.date.strftime("%A, %B %d, %Y")}.</p>
</div>
<ul>
<% section = "start" %>
%for mitem in meeting.meeting_items:
    <li class="hubby-meeting-item">
      %if mitem.type != section:
         <% section = mitem.type or "unknown" %>
	  <h3>${mitem.type.capitalize()} Agenda</h3><br/>
      %endif
      <b>${mitem.item.file_id}: ${mitem.item.name}</b><br/>
      <p class="hubby-meeting-item-status">Status:  ${mitem.item.status}</p>
      <p class="hubby-meeting-item-text">${mitem.item.title}</p>
      <!--
      <ul class="hubby-meeting-item-attachments">
	%for att in mitem.item.attachments:
	    <li>${att.name}</li>
	%endfor
      </ul>
      -->
      <hr/>
    </li>
%endfor
</ul>
</div>
