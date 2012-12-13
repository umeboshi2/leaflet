$(document).ready(function() {

    $('.hubby-meeting-item-attachments').hide()
    $('.hubby-meeting-item-attachment-marker').click(function() {
	$(this).next().toggle()
    });    
    $('.hubby-meeting-item-action-marker').click(function() {
	var itemid = $(this).attr('id');
	$(this).next().load('/hubbyjax/itemactions/' + itemid);
	$(this).replaceWith(itemid)
    });
});
