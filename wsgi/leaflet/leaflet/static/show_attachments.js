$(document).ready(function() {
    //$('.hubby-meeting-item').draggable()    
    $('.hubby-meeting-item-attachments').hide()
    $('.hubby-meeting-item-attachments').draggable()
    $('.hubby-meeting-item-info').click(function() {
	$(this).next().toggle()
    });
    $('.hubby-meeting-item-attachment-marker').click(function() {
	$(this).next().toggle()
    });    
    $('.hubby-meeting-item-action-marker').click(function() {
	if ($(this).hasClass('itemaction-loaded'))
	{
	    $(this).next().toggle()
	}
	else
	{
	    var itemid = $(this).attr('id');
	    $(this).next().load('/hubbyjax/itemactions/' + itemid);
	    //$(this).replaceWith(itemid)
	    $(this).addClass('itemaction-loaded');
	}
    });
});
