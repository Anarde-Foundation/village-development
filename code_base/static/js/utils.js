var appUtils = ( function(){
    var formatDate = function(dt) {
        if (dt == null) return '-';
        return moment(dt).format("MMMM DD, YYYY");
    };

     var formatDateTime = function(dt) {
        if (dt == null) return '-';
        return moment(dt).format("MMMM DD, YYYY HH:mm:ss");
     };

    var formatDatatableDate = function(data, type, row) {
        if (data == null) return '-';
        return '<span class="d-none">'+ data +'</span>' + formatDate(data);
        //return data;
    };

    var formatDatatableDateTime = function(data, type, row) {
        if (data == null) return '-';
        return '<span class="d-none">'+ data +'</span>' + formatDateTime(data);
        //return data;
    };

    var navigateToUrl = function(url) {
        window.location = url;
    };

    return {
       formatDatatableDate: formatDatatableDate,
       formatDatatableDateTime: formatDatatableDateTime,
       navigateToUrl: navigateToUrl
    };
}) ();