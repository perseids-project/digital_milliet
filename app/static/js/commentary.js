$('#lang_tabs a').click(function (e) {
	e.preventDefault()
	$(this).tab('show')
})

$('#lang_tabs a[href="#english"]').tab('show')
$('#lang_tabs a[href="#french"]').tab('show')
$('#lang_tabs a[href="#commentary"]').tab('show')
$('#lang_tabs a[href="#bibliography"]').tab('show')


function get_cts(textURI, textType){
	var endpoint = new CTS.endpoint.XQ("http://sosol.perseids.org/exist/rest/db/xq/CTS.xq?");
	var cts_obj = new CTS.text.Passage(textURI, endpoint, "annotsrc")
	cts_obj.retrieve({
		success : function(data) {
            if(cts_obj.checkXML() === true) {

              var name = cts_obj.getXml("groupname", "xml")[0].textContent;
              var title = cts_obj.getXml("label", "xml")[0].textContent;
              var psg = cts_obj.getXml("psg", "xml")[0].textContent;
              $('#auth_head').html("<h2>"+name+", "+title+", "+psg+"</h2>");
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

