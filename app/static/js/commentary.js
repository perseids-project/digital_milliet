$('#lang_tabs a').click(function (e) {
	e.preventDefault()
	$(this).tab('show')
})

$('#lang_tabs a[href="#english"]').tab('show')
$('#lang_tabs a[href="#french"]').tab('show')
$('#lang_tabs a[href="#commentary"]').tab('show')
$('#lang_tabs a[href="#bibliography"]').tab('show')


function get_cts(textURI, textType){
	var endpoint = new CTS.endpoint.XQ("http://services2.perseids.org/exist/restxq/cts?");
	var cts_obj = new CTS.text.Passage(textURI, endpoint, "annotsrc")
	cts_obj.retrieve({
		success : function(data) {
            if(cts_obj.checkXML() === true) {

              var psg = cts_obj.getXml("psg", "xml")[0].textContent;
              $("#"+textType+" p").html(cts_obj.getXml("body", "string"));

            } else {
              $("#"+textType+" p").html("We are sorry, this text is not availible at this time");
            }
          },
	      error :  function(status, statusText) {
	        console.log(status, statusText); // For debug
	      }

	});
}

