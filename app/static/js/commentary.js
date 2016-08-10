

$('#lang_tabs a').click(function (e) {
	e.preventDefault()
	$(this).tab('show')
})

$('#lang_tabs a[href="#eng"]').tab('show')
$('#lang_tabs a[href="#fra"]').tab('show')
$('#lang_tabs a[href="#commentary"]').tab('show')
$('#lang_tabs a[href="#bibliography"]').tab('show')


function get_cts(textURI, textType){
	var endpoint = new CTS.endpoint.XQ("http://cts.perseids.org/api/cts/?");
	var cts_obj = new CTS.text.Passage(textURI, endpoint, "digmill")
	cts_obj.retrieve({
		success : function(data) {
            if(cts_obj.checkXML() === true) {

              var psg = cts_obj.getXml("passage", "xml")[0].textContent;
              $("#"+textType+" p").html(psg);

            } else {
              $("#"+textType+" p").html("We are sorry, this text is not availible at this time");
            }
          },
	      error :  function(status, statusText) {
	        console.log(status, statusText); // For debug
	      }

	});
}

function set_active() {
	$('#lang_tabs a').each(function() {
	  if ($('#' + this.getAttribute('aria-controls')+ ' p')[0].innerHTML.length > 0) {
	    $(this).addClass("active").tab('show');
	    return false;
	  }
	});
};