/*
 * All Endpoints need to have at least the following:
 * annotationsList - current list of OA Annotations
 * dfd - Deferred Object
 * init()
 * search(options, successCallback, errorCallback)
 * create(oaAnnotation, successCallback, errorCallback)
 * update(oaAnnotation, successCallback, errorCallback)
 * deleteAnnotation(annotationID, successCallback, errorCallback) (delete is a reserved word)
 * TODO:
 * read() //not currently used
 *
 * Optional, if endpoint is not OA compliant:
 * getAnnotationInOA(endpointAnnotation)
 * getAnnotationInEndpoint(oaAnnotation)
 */
(function($){

  $.MillietEndpoint = function(options) {

    jQuery.extend(this, {
      search_uri:    function() {},
      delete_uri:    function() {},
      create_uri:    function() {},
      update_uri:    function() {},
      authorized:    null,
      annotationsList: [],        //OA list for Mirador use
      annotationsListCatch: null,  //internal list for module use
      windowID: null,
      eventEmitter: null
    }, options);

    this.init();
  };

  $.MillietEndpoint.prototype = {
    //Set up some options for catch
    init: function() { },

    set: function(prop, value, options) {
      if (options) {
        this[options.parent][prop] = value;
      } else {
        this[prop] = value;
      }
    },

    //Search endpoint for all annotations with a given URI
    search: function(options, successCallback, errorCallback) {
      var _this = this;
      this.annotationsList = []; //clear out current list

      jQuery.ajax({
        url: _this.search_uri(),
        type: 'GET',
        dataType: 'json',
        data: {
          uri: options.uri,
          text : options.text ? options.text : undefined,
          tag : options.tag ? options.tag : undefined,
          parentid : options.parentid ? options.parentid : undefined,
          contextId: _this.context_id,
          collectionId: _this.collection_id,
          media: options.media ? options.media : "image",
          limit: options.limit ? options.limit : -1
        },

        contentType: "application/json; charset=utf-8",
        success: function(data) {
          //check if a function has been passed in, otherwise, treat it as a normal search
          if (typeof successCallback === "function") {
            successCallback(data);
          } else {
            var annotationsLists = data;
            jQuery.each(annotationsLists, function(index, value) {
              _this.annotationsList.push(_this.getAnnotationInOA(value));
            });
            _this.dfd.resolve(true);
            _this.eventEmitter.publish('catchAnnotationsLoaded.'+_this.windowID, annotationsLists);
          }
        },
        error: function() {
          if (typeof errorCallback === "function") {
            errorCallback();
          } else {
            console.log("There was an error searching this endpoint");
          }
        }

      });
    },

    deleteAnnotation: function(annotationID, successCallback, errorCallback) {
      var _this = this;
      jQuery.ajax({
       url: this.delete_uri(annotationID),
       type: 'DELETE',
       dataType: 'json',
       contentType: "application/json; charset=utf-8",
       success: function(data) {
        if (typeof successCallback === "function") {
          successCallback();
        }
        _this.eventEmitter.publish('catchAnnotationDeleted.'+_this.windowID, annotationID);
      },
      error: function() {
        if (typeof errorCallback === "function") {
          errorCallback();
        }
      }

    });
    },

    update: function(oaAnnotation, successCallback, errorCallback) {
      var annotations = this.getAnnotationInEndpoint(oaAnnotation),
      _this = this;

      annotations.forEach(function(annotation) {
        var annotationID = annotation.id;

        jQuery.ajax({
          url: _this.update_uri(annotationID),
          type: 'POST',
          dataType: 'json',
          data: JSON.stringify(annotation),
          contentType: "application/json; charset=utf-8",
          success: function(data) {
            if (typeof successCallback === "function") {
              successCallback(_this.getAnnotationInOA(data));
            }
            _this.eventEmitter.publish('catchAnnotationUpdated.'+_this.windowID, annotation);
          },
          error: function() {
            if (typeof errorCallback === "function") {
              errorCallback();
            }
          }
        });
      });
    },

    //takes OA Annotation, gets Endpoint Annotation, and saves
    //if successful, MUST return the OA rendering of the annotation
    create: function(oaAnnotation, successCallback, errorCallback) {
      this.createAnnotation(oaAnnotation, successCallback, errorCallback);
    },

    createAnnotation: function(catchAnnotation, successCallback, errorCallback) {
      var _this = this;

      jQuery.ajax({
        url: this.create_uri(),
        type: 'PUT',
        dataType: 'json',
        data: JSON.stringify(catchAnnotation),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
          if (typeof successCallback === "function") {
            successCallback(data);
          } else {
              _this.annotationsList.push(data)
              _this.dfd.resolve(true);
          }
          _this.eventEmitter.publish('catchAnnotationCreated.'+_this.windowID, data);
        },
        error: function() {
          if (typeof errorCallback === "function") {
            errorCallback();
          }
        }
      });
    },

    userAuthorize: function(action, annotation) {
      return this.authorized;
    },

    //Convert Endpoint annotation to OA
    getAnnotationInOA: function(annotation) {
      annotation.endpoint = this;
      return annotation;
    },

    // Converts OA Annotation to endpoint format
    getAnnotationInEndpoint: function(oaAnnotation) {
      return oaAnnotation;
    }
  };

}(Mirador));
