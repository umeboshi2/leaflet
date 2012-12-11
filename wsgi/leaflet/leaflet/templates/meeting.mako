<div class="hubby-meeting">
<p>Department: ${meeting.dept.name}.</p>
<p>Meeting for ${str(meeting.date)}.</p>
<ul>
%for mitem in meeting.meeting_items:
    <li class="hubby-meeting-item">
      ${mitem.item.file_id}: ${mitem.item.name}<br/>
      <style "font-size:0.8em"><p>${mitem.item.title}</p></style>
      <ul>
	%for att in mitem.item.attachments:
	    <li>${att.name}<li>
	%endfor
      </ul>
    </li>
%endfor
</ul>
</div>
