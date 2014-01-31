$(document).ready ->
    $('.hubby-meeting-item-attachments').hide()
    $('.hubby-meeting-item-attachments').draggable()
    $('.hubby-meeting-item-info').click ->
        $(this).next().toggle()
    $('.hubby-meeting-item-attachment-marker').click ->
        $(this).next().toggle()
    $('.hubby-meeting-item-action-marker').click ->
        if $(this).hasClass('itemaction-loaded')
            $(this).next().toggle()
        else
            itemid = $(this).attr('id')
            url = '/hubby/frag/itemactions/' + itemid
            $(this).next().load(url)
            $(this).addClass('itemaction-loaded')
