<div class="hubby-tagged-items">
<div class="hubby-tagged-items-header">
</div>
<div class="hubby-tagged-items-list">
%for item in items:
	<div class="hubby-meeting-item">
	  <div class="hubby-meeting-item-info">
	    <div class="hubby-meeting-item-fileid">${item.file_id}</div>
	    <!--<div>${item.name}</div>-->
	    <div class="hubby-meeting-item-status">${item.status}</div>
	  </div>
	  <div class="hubby-meeting-item-content">
	    <p class="hubby-meeting-item-text">${item.title}</p>
	    %if item.attachments:
	    <div class="hubby-meeting-item-attachment-marker">Attachments</div>
	    <div class="hubby-meeting-item-attachments">
	      <div class="hubby-meeting-item-attachments-header">Attachments</div>
	      %for att in item.attachments:
	      <div><a href="${att.get_link()}">${att.name}</a></div>
	      %endfor
	    </div>
	    %endif
	    %if item.actions:
	    <div class="hubby-meeting-item-action-marker" id="${item.id}" onclick="${request.route_url('hubby_frag', context='itemactions', id=item.id)}">Actions</div>
	    <div class="hubby-meeting-item-actions"></div>
	    %endif
	  </div>
	</div>
%endfor
</div>
</div>
