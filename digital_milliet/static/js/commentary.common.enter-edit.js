
var remove_input = function(target) {
  target.remove();
};
var add_input = function(model, target) {
      var formgroup = $(model[0]).clone();
      formgroup.attr("id", "");
      formgroup.find(".add-input").on("click", function (e) {
          e.preventDefault();
          add_input(model, target);
      });
      formgroup.find(".rem-input").on("click", function (e) {
          e.preventDefault();
          remove_input(formgroup);
      });

      target.append(formgroup);

  };

let tagsbh = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  local: [ ],
  remote: {
    url: '/api/tags/text',
  }
});

let semtagsbh = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  local: [ ],
  remote: {
    url: '/api/tags/semantic',
  }
});

tagsbh.initialize();
semtagsbh.initialize();

function initialize_tag_typeahead() {
  $(".tags.typeahead").typeahead(null, {
    name: 'tags-remote',
    display: 'value',
    source: tagsbh.ttAdapter()
  });

}

function initialize_semantic_tag_typeahead() {
  $(".semantic-tags.typeahead").typeahead(null, {
    name: 'semantic-tags-remote',
    display: 'value',
    source: semtagsbh.ttAdapter()
  });
}
