<div class="hubby-short-action">
  %if action.mover is not None:
<p>Mover: ${ '%s %s' % (action.mover.firstname, action.mover.lastname)} &nbsp; Seconder: ${ '%s %s' % (action.seconder.firstname, action.seconder.lastname)}</p>
  %endif
<p class="hubby-action-text">${action.action_text.replace('\n', '<br/>')|n}</p>
</div>
