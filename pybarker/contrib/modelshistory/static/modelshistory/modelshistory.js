$(function () {
	"use strict";

	$( document ).on( "click", ".fieldhistory", function() {
		var cdvs = $(this);
		var fpk = cdvs.closest("[data-modelshistory-model-pk]").data('modelshistory-model-pk');
		// имя поля либо прописано в самой кнопке либо берётся name предыдущего поле-инпута
		var fname = cdvs.data('modelshistory-fieldname');
		if (typeof fname == 'undefined') {
			var prevcontrol = cdvs.prev();
			if(prevcontrol.hasClass('select2')) // для select2 настоящий select ещё предыдущий
			{
				prevcontrol = prevcontrol.prev();
			}
			fname = prevcontrol.attr('name');
		}
		if (typeof fname == 'undefined' || fname == null) {
			alert('error found name field for entity pk=' + fpk);
			return;
		}
		var model_pk_field = fpk+"-"+fname;
		openSimpleDialog({
			title: 'История изменения поля',
			url: '/modelshistory/field_history/'+model_pk_field+'/',
			//data
			//afterFillCall
		});
	});	
});