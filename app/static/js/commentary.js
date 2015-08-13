$('#lang_tabs a').click(function (e) {
	e.preventDefault()
	$(this).tab('show')
})

$('#lang_tabs a[href="#english"]').tab('show')
$('#lang_tabs a[href="#french"]').tab('show')
$('#lang_tabs a[href="#commentary"]').tab('show')
$('#lang_tabs a[href="#bibliography"]').tab('show')

$(document).ready(function() {
	var textURI = $("").val(),
      endpoint = new CTS.endpoint.simpleUrl(textURI);
});
