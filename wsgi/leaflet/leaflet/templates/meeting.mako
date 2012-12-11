<div class="hubby-meeting">
<div class="hubby-meeting-header">
  <p>Department: ${meeting.dept.name}.</p>
  <p>Meeting for ${meeting.date.strftime("%A, %B %d, %Y")}.</p>
</div>
<ul>
%for mitem in meeting.meeting_items:
    <li class="hubby-meeting-item">
      ${mitem.item.file_id}: ${mitem.item.name}<br/>
      <p>Status:  ${mitem.item.status}</p>
      <p><style "font-size:0.8em;">${mitem.item.title}</style></p>
      <ul class="hubby-meeting-item-attachments">
	%for att in mitem.item.attachments:
	    <li>${att.name}</li>
	%endfor
      </ul>
      <hr/>
    </li>
%endfor
</ul>
</div>
