var rimsview = (function() {
    
    //$('#include-nav').load('nav.html');
    //$('#include-search-params').load('search-params.html');
    
    // Private Variables
    var singleDayQuery = true;
    var cameraID = 0;
    var loadedCounter = 0;
    var cameraNames = ["PTVR01HM","PTVR01LM","PTVR02HM","PTVR02LM","PTVR03HM","PTVR03LM"];
    var imagePostfix = ['.jpg','_binary.png','_boundary.png','.png'];
    var imagePostfixIndex = 0;
    var cameraRes = [0.86/1000, 6.9/1000, 0.86/1000, 6.9/1000, 0.86/1000/1000, 6.9/1000];
    var dataLoaded = false;
    var siteURL = "http://deeprip.shore.mbari.org";
    var newSiteURL = "http://deeprip.shore.mbari.org";
    var roiImagesBase = "rims-ptvr/rois/images/";
    var roiArchiveBase = "rims-ptvr/rois/imagearchive/";
    var dailyStatsBase = "rims-ptvr/roistats/dailystats/";
    var viewerBase  = '/static/rimsview/rimsview.html';
    var dailyStats = [];
    var allLabels = [];
    var allTags = [];
    var dailyStatsIndex = 0;
    
    // Retrieve elements for UI
    // Container for image mosaic using isotope
    var toolsNav = $('#tools-nav');
    var mosaicContainer = $('#MosaicContainer');
    var statusBar = $('#status-bar');
    var statusText = $('#status-text');
    var queryText = $('#query-text');
    var timeline = $('#timeline');
    var timelineToggle = $('#toggle-timeline');
    var searchParamsToggle = $('#toggle-search-params');
    var searchLabelParamsToggle = $('#toggle-label-params');
    var runSearch = $('#run-search');
    //var getArchive = $('#get-archive');
    var searchByName = $('#search-by-name');
    var runNamedSearch = $('#run-named-search');
    var nImages = $('#n-images');
    var minMaj = $('#min-maj');
    var maxMaj = $('#max-maj');
    var minAspect = $('#min-aspect');
    var maxAspect = $('#max-aspect');
    var excludeClipped = $('#exclude-clipped');
    var searchMachineLabels = $('#search-machine-labels');
    var searchInvertLabels = $('#search-invert-labels');
    var searchHumanLabels = $('#search-human-labels');
    var randomizeResults = $('#randomize-results');
    //var makeArchive = $('#make-archive');
    var hideLabeled = $('#hide-labeled');
    var hideTagged = $('#hide-tagged');
    var camera = $('#camera');
    var searchLabel = $('#search-label');
    var searchAnnotator = $('#search-annotator');
    var searchTag = $('#search-tag');
    var utcStart = $('#utc-start');
    var utcEnd = $('#utc-end');
    var minDepth = $('#min-depth');
    var maxDepth = $('#max-depth');
    //var hourStart = $('#hour-start');
    //var hourEnd = $('#hour-end');
    var labelSelect = $('#label');
    var tagSelect = $('#tag');
    var username = '';
    var isAuthenaticated = false;
    var startedTime = 0;


    var lastQueryUrl = '';

    var queryPresets = [
        {
            "name": "Ahi 11 i2MAP LM",
            "label": "LRAH-11-LM",
            "title": "Images from the Ahi 11 Deployment Low-Mag Camera",
            "camera": "PTVR02LM",
            "minmaj": 0.5,
            "maxmaj": 5.0,
            "minasp": 0.5,
            "maxasp": 1.0,
            "utcStart": "2024-03-20 12:00:00",
            "utcEnd": "2024-03-21 12:00:00",
        },
        {
            "name": "Ahi 11 i2MAP HM",
            "label": "LRAH-11-HM",
            "title": "Images from the Ahi 11 Deployment High-Mag Camera",
            "camera": "PTVR02HM",
            "minmaj": 0.03,
            "maxmaj": 1.0,
            "minasp": 0.1,
            "maxasp": 1.0,
            "utcStart": "2024-03-20 12:00:00",
            "utcEnd": "2024-03-21 12:00:00",
        },
        {
            "name": "Ahi 12 Synchro Medium Round",
            "label": "LRAH-12-SYNC-MR",
            "title": "Images from the Ahi 12 Deployment of medium round objects",
            "camera": "PTVR02LM",
            "minmaj": 0.5,
            "maxmaj": 2.0,
            "minasp": 0.6,
            "maxasp": 1.0,
            "utcStart": "2024-04-15 00:00:00",
            "utcEnd": "2024-04-16 12:00:00",
        },
        {
            "name": "Ahi 12 Synchro Small Round",
            "label": "LRAH-12-SYNC-SR",
            "title": "Images from the Ahi 12 Deployment of small round objects",
            "camera": "PTVR02HM",
            "minmaj": 0.03,
            "maxmaj": 2.0,
            "minasp": 0.6,
            "maxasp": 1.0,
            "utcStart": "2024-04-15 00:00:00",
            "utcEnd": "2024-04-16 12:00:00",
        },
    ];

    var imageDetailActive = false;
    
    // Set Defaults
    nImages.val('5000');
    minMaj.val('.5');
    maxMaj.val('5');
    minAspect.val('.05');
    maxAspect.val('1');
    camera.val("0");
    minDepth.val("0.0");
    maxDepth.val("300.0");
    //hourStart.val("0");
    //hourEnd.val("24");
    excludeClipped.prop('checked',true);
    hideLabeled.prop('checked',true);
    hideTagged.prop('checked',true);
    
    searchLabel.val("Any")
    searchTag.val("Any")    
    // Hide Alerts
    $('.alert').hide();

    $('.dropdown-menu').find('form').click(function (e) {
        e.stopPropagation();
    });



    d1 = new Date();
    utcStart.val('11/01/2021 00:00:00');
    utcEnd.val(' 12/30/2024 23:59:59');

    //var queryStartTime = 0;
    var queryStartTime = 0;

    function getBaseURL() {
        if (queryStartTime >= 1501574400000)
            return newSiteURL;
        else
            return siteURL;
    }

    //utcStart.val('04/14/2014');
    //utcEnd.val('04/15/2014');
    camera.val(cameraID); 
    
    function getCameraName(image_id) {
        stmp = image_id.split('_');
        
        cameraName = stmp[2];

        return cameraName;
    
    }
    
    function showLogin() {
        $('#tool-login').show();
        $('#tools-nav').empty();
        $('#sign-in').on("click",function() {
            loginUser($('#username').val(),$('#password').val());
        });

    };

    function logoutUser() {
        prepAjax();
        data = {'user': username};
        $.ajax({
            url: siteURL + '/rims-ptvr/rois/logout_user',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            processData: false,
            data: JSON.stringify(data),
            success: function(result) {
                //console.log(result);
                // mark selected images as labeled or tagged from result
                showLogin();        
                isAuthenticated = false;
                $('.selected-image-item').removeClass('selected-image-item');
                $('#AnnotationTools').addClass('collapse');
            }
        });
    };

    function showTools() {  

        $('#tool-login').hide();
        $('#tools-nav').empty();
        $('#tools-nav').append('<li id="toggle-tools"><a href="#">Tools</a></li>');

        $('#tools-nav').append('<li id="logout-tools"><a href="#">Logout ('+username+')</a></li>');

        $('#toggle-tools').on("click",function() {
            if(isAuthenticated) {
                //add the options to label and tag select boxes
                $('#AnnotationTools').toggleClass('collapse');
            }
        });

        $('#logout-tools').on("click",function() {
            logoutUser();
        });
    };
    
    function getUser() {
        $.ajax({
            url: siteURL + '/rims-ptvr/rois/get_user',
            type: 'GET',
            success: function (json) {
                isAuthenticated = json['is_authenticated'];
                username = json['username'];

                //console.log(json);

                if (isAuthenticated) {
                    showTools();
                }
                else {
                    showLogin();
                }
            },
        });

    };
    
    function loginUser(user,pass) {
        prepAjax();
        data = {'username': user, 'password': pass};
        $.ajax({
            url: siteURL + '/rims-ptvr/rois/login_user',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            processData: false,
            data: JSON.stringify(data),
            success: function(result) {
                // mark selected images as labeled or tagged from result
                getUser();
                //console.log(result);
            }
        });
    };


    //CSRF helpers
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    
    function prepAjax() {    
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                var csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    };


    // Debouncer to throttle event triggers
    function debouncer( func , timeout ) {
        var timeoutID , timeout = timeout || 200;
        return function () {
            var scope = this , args = arguments;
            clearTimeout( timeoutID );
            timeoutID = setTimeout( function () {
                func.apply( scope , Array.prototype.slice.call( args ) );
            } , timeout );
        }
    };  

    // Pad a number n with zeros up to len
    function zpad(n,len) {
        return ('0000000000000000'+n).slice(-len);
    };
    
    // convert date in format MM/DD/YYYY hh:mm:ss to unixtime
    function dateStringtoUnixtime(d) {
        // use javascript Date, but first subtract 1 from month
        // Use PST for conversion, daylight savings time corrected
        // on server if needed
        //tdate = parseInt(d);
        tdate = Date.parse(d + ' PST');
        if (isNaN(tdate)) {
            //date time might be already in unixtime
            ut = parseInt(d);
            if (ut > 1394323200) {
                return ut*1000;
            }
        }
        else
            return tdate;
    };
    
    function trueMonth(m) {
        return m +1;
    };
    
    

    
    // Query URLs
    function buildQueryURL() {
    
        var cameraIndex = camera.val();
        var name = cameraNames[cameraIndex];
        var res = cameraRes[cameraIndex];
    
        queryStartTime = dateStringtoUnixtime(utcStart.val());

        input_url = getBaseURL() + "/" + roiImagesBase;
        input_url = input_url + name + "/";
        input_url = input_url + dateStringtoUnixtime(utcStart.val()) + "/";
        input_url = input_url + dateStringtoUnixtime(utcEnd.val()) + "/";
        input_url = input_url + '0' + "/";
        input_url = input_url + '24' + "/";
        input_url = input_url + minDepth.val() + "/";
        input_url = input_url + maxDepth.val() + "/";
        input_url = input_url + nImages.val() + "/";
        input_url = input_url + Math.floor(minMaj.val()/res) + "/";
        input_url = input_url + Math.ceil(maxMaj.val()/res) + "/";
        input_url = input_url + minAspect.val() + "/";
        input_url = input_url + maxAspect.val() + "/";
        if(excludeClipped.prop('checked'))
            input_url = input_url + "clipped/";
        else
            input_url = input_url + "noexclude/";
        if(randomizeResults.prop('checked'))
            input_url = input_url + "randomize/";
        else
            input_url = input_url + "ordered/";
        //if(makeArchive.prop('checked'))
        //    input_url = input_url + "archive/";
        //else
            input_url = input_url + "skip/";
        invertString = '';
        if (searchInvertLabels.prop('checked')) {
          invertString = '!';
        }

        input_url = input_url + invertString + searchLabel.val() + "/";
        labelType = "anytype";
        if(searchMachineLabels.prop('checked') && !searchHumanLabels.prop('checked'))
            labelType = "machines";
        else if(searchHumanLabels.prop('checked') && !searchMachineLabels.prop('checked'))
            labelType = "humans";
        input_url = input_url + labelType + "/";
        input_url = input_url + searchTag.val() + '/';
        input_url = input_url + searchAnnotator.val() + '/';
        console.log(input_url);
        return input_url;
    };
    
    function buildArchiveURL() {
    
        var cameraIndex = camera.val();
        var name = cameraNames[cameraIndex];
        var res = cameraRes[cameraIndex];
    
        input_url = roiArchiveBase;
        input_url = input_url + name + "/";
        input_url = input_url + dateStringtoUnixtime(utcStart.val()) + "/";
        input_url = input_url + dateStringtoUnixtime(utcEnd.val()) + "/";
        input_url = input_url + '0' + "/";
        input_url = input_url + '24' + "/";
        input_url = input_url + Math.floor(minMaj.val()/res) + "/";
        input_url = input_url + Math.ceil(maxMaj.val()/res) + "/";
        input_url = input_url + minAspect.val() + "/";
        input_url = input_url + maxAspect.val() + "/";
        if(excludeClipped.prop('checked'))
            input_url = input_url + "clipped/";
        else
            input_url = input_url + "noexclude/";
        input_url = input_url + searchLabel.val() + "/";
        input_url = input_url + 'any/';
        //console.log(input_url);
        return input_url;
    };

    function checkIntInput(input,minVal,maxVal) {
        var allOkay = true;
        var result = parseInt(input.val());
        //console.log(result);
        if (isNaN(result)) {
            input.addClass('list-group-item-danger');
            allOkay = false;
        } 
        else if (result < minVal) {
            input.val(minVal);
            input.removeClass('list-group-item-danger');
        }
        else if (result > maxVal) {
            input.val(maxVal);
            input.removeClass('list-group-item-danger');
        }
        else {
            input.val(result);
            input.removeClass('list-group-item-danger');
        }

        return allOkay;
    }
    
    function checkFloatInput(input,minVal,maxVal) {
        var allOkay = true;
        var result = parseFloat(input.val());
        //console.log(result);
        if (isNaN(result)) {
            input.addClass('list-group-item-danger');
            allOkay = false;
        } 
        else if (result < minVal) {
            input.val(minVal);
            input.removeClass('list-group-item-danger');
        }
        else if (result > maxVal) {
            input.val(maxVal);
            input.removeClass('list-group-item-danger');
        }
        else {
            input.val(result);
            input.removeClass('list-group-item-danger');
        }

        return allOkay;
    }

    function checkFloatRange(inputLow,inputHigh) {
        var allOkay = true;
        var result1 = parseFloat(inputLow.val());
        var result2 = parseFloat(inputHigh.val());

        if (result2 <= result1) {
            inputLow.addClass('list-group-item-danger');
            inputHigh.addClass('list-group-item-danger');
            allOkay = false;
        }

        return allOkay;
    };


    function checkDatetimeInput(input) {
        var allOkay = true;
        var result = dateStringtoUnixtime(input.val());
        if (isNaN(result)) {
            input.addClass('list-group-item-danger');
            allOkay = false;
        }
        else {
            input.removeClass('list-group-item-danger');
            allOkay = true;
        }
        return allOkay;
    }
    
    function checkDateRange(inputStart,inputEnd) {
        var allOkay = true;
        var result1 = dateStringtoUnixtime(inputStart.val());
        var result2 = dateStringtoUnixtime(inputEnd.val());

        if (result2 <= result1) {
            inputStart.addClass('list-group-item-danger');
            inputEnd.addClass('list-group-item-danger');
            allOkay = false;
        }
        return allOkay;
    }

    // Clear mosaics and progress bars
    function clearContainers() {
        mosaicContainer.html("");
        $('.image-item').remove();
    }
    
    // Update the search datetime
    function updateSearchDateTime(timestamp) {
        $('#timeline').highcharts().xAxis[0].removePlotLine('selected-line');
        $('#timeline').highcharts().xAxis[0].addPlotLine({
            value: timestamp,
            width: 5,
            color: '#FFF',
            id: 'selected-line'
        });
        dataLoaded = false;
        var d1 = new Date((Math.floor(timestamp)));
        utcStart.val(zpad(trueMonth(d1.getMonth()),2)+"/"+zpad(d1.getDate(),2)+"/"+d1.getFullYear()+' 00:00:00');
        utcEnd.val(zpad(trueMonth(d1.getMonth()),2)+"/"+zpad(d1.getDate(),2)+"/"+d1.getFullYear()+' 23:59:59');
    }
    
    function updateDateTimeHover(x,y) {
        var d1 = new Date((Math.floor(x)));
        var dateString = zpad(trueMonth(d1.getMonth()),2)+"/"+zpad(d1.getDate(),2)+"/"+d1.getFullYear();
        var counts = zpad(y,10);
        statusText.html("Date: " + dateString + ", detected rois: " + counts);
    }
    
    // Shows a warning message in the status bar
    function showServerLoading() {
        statusBar.width("100%");
        statusBar.addClass('progress-bar-warning');
        statusBar.addClass('progress-bar-striped');
        statusBar.addClass('active');
        statusBar.css("color","#fff");
        //if(makeArchive.prop('checked'))
        //    statusBar.html('Loading data from server and making downloadable archive...this may take some time...');
        //else
            statusBar.html('Loading data from server...');
    };
    
    // Shows a warning message in the status bar
    function clearServerLoading() {
        statusBar.width("100%");
        statusBar.removeClass('progress-bar-warning');
        statusBar.removeClass('progress-bar-striped');
        statusBar.removeClass('active');
        statusBar.css("color","#FF0");
        statusBar.addClass('progress-bar-primary');
    };
    
    // Render query string from settings
    function renderQueryString(JSONData) {
        var dStart = utcStart.val();
        var dEnd = utcEnd.val();
        var currentPage = 1;
        var nextPage = JSONData.image_data.next;
        var previousPage = JSONData.image_data.previous;
        var pageSize = JSONData.page_size;
        if (nextPage != null) {
            currentPage = parseInt(nextPage.split('?page=')[1]) - 1;
        }     
        else if (previousPage != null) {
            currentPage = parseInt(previousPage.split('?page=')[1]) + 1;
        }
                
        out = "<b>Query: Major Axis (mm) ["+minMaj.val()+","+maxMaj.val()+"],";
        out = out + " Aspect Ratio ["+minAspect.val()+","+maxAspect.val()+"],";
        out = out + " Date Range " + dStart;
        out = out + " to " + dEnd;
        out = out + ". Found " + JSONData.image_data.count + " rois, showing " 
            + (currentPage-1)*pageSize + " to " + currentPage*pageSize + "</b>";
        
        return out;
    };
    
    function updateDetailImage(data) {
        
        if (!imageDetailActive)
            return;
   
        // get the camer name
        camName = getCameraName(data.image_id)

        //var cameraIndex = camera.val();
        var res = cameraRes[cameraNames.indexOf(camName)];
        
        var base_url = getBaseURL()+ "/" + data.image_url;
        var image_url = base_url + imagePostfix[imagePostfixIndex];
        $('#TargetImg').attr("src",image_url);
        // Compute Image size from ImageDetail Container 
        var aspectRatio = data.image_height/data.image_width;
        var heightScale = $('#ImageDetail').height()/data.image_height;
        var widthScale = $('#ImageDetail').width()/data.image_width;
        if (data.image_width*heightScale > 0.6*$('#ImageDetail').width()) {
            // Scale Image by width
            $('#TargetImg').width(0.6*$('#ImageDetail').width());
            $('#TargetImg').height(0.6*$('#ImageDetail').width()*aspectRatio);
        }
        else {
            $('#TargetImg').height(0.75*$('#ImageDetail').height());
            $('#TargetImg').width(0.75*$('#ImageDetail').height()/aspectRatio);
            
        }
        var scaleInfo = data.image_width*res;
        $('#ScaleBar').html(scaleInfo.toPrecision(3) + " mm");
        $('#ScaleBar').width($('#TargetImg').width());
        $('#ImageDetailTitle').html(image_url);

        // Info
        //console.log(data);
        $('#ImageName').html("<h6 class='info-label'>Image ID</h6>" + "<h5>" + data.image_id + "</h5>");
        $('#Timestamp').html("<h6 class='info-label'>Collection Datetime</h6>" + "<h5>" + data.image_timestamp + "</h5>");
        $('#MajorAxisLength').html("<h6 class='info-label'>Major Axis Length</h6>" + "<h5>" + (data.major_axis_length*res).toFixed(2) + " mm</h5>");
        $('#MinorAxisLength').html("<h6 class='info-label'>Minor Axis Length</h6>" + "<h5>" + (data.minor_axis_length*res).toFixed(2) + " mm</h5>");
        $('#AspectRatio').html("<h6 class='info-label'>Aspect Ratio </h6>" + "<h5>" + (data.aspect_ratio).toFixed(2) + "</h5>");
        $('#Depth').html("<h6 class='info-label'>Depth </h6>" + "<h5>" + (data.depth).toFixed(2) + " m </h5>");
        $('#Temperature').html("<h6 class='info-label'>Temperature </h6>" + "<h5>" + (data.temperature).toFixed(2) + " C</h5>");
        $('#Chlorophyll').html("<h6 class='info-label'>Chlorophyll </h6>" + "<h5>" + (data.chlorophyll).toFixed(3) + " ug/l</h5>");
        $('#Latitude').html("<h6 class='info-label'>Latitude </h6>" + "<h5>" + (data.latitude).toFixed(5) + " deg.</h5>");
        $('#Longitude').html("<h6 class='info-label'>Longitude </h6>" + "<h5>" + (data.longitude).toFixed(5) + " deg.</h5>");
    };
    
    function addImageFromZip(zip,data,imagePath,buttonObj,imageObj) {
    
        if (zip.file(imagePath)) {
            zip.file(imagePath).async("arraybuffer").then(function success(content) {

                var imgBlob = new Blob([content]);
                var zipImgURL = this.URL.createObjectURL(imgBlob);
            
                $(buttonObj).on('click', data, function (event) {

                    //console.log(zipImgURL);
                    $(imageObj).attr("src",zipImgURL);
                    //data.imageObj.attr("title",data.imagePath);
                    //data.imageObj.attr("srcset",data.imagePath);
                });
            }, function error(e) {
                console.log(e);
            });
        }
    }
     
    function showImageDetail(data) {
        // Otherwise show image detail
        //var data = this.roi_data;
        var base_url = getBaseURL() + "/" + data.image_url;

        // get archive data and extract to temperature containers
        JSZipUtils.getBinaryContent(base_url+'.zip', function (err, zipdata) {
            if(err) {
                throw err; // or handle the error
            }

            JSZip.loadAsync(zipdata).then(function(zip) {
                pathArray = data.image_url.split('/');
                filename = pathArray[pathArray.length - 1];
                var imagePath = filename+'_binary.png';
                addImageFromZip(zip,data,imagePath,'#ShowBinaryImage','#TargetImg');
                var imagePath = filename+'_rawcolor.png';
                addImageFromZip(zip,data,imagePath,'#ShowRawImage','#TargetImg');

            });
        });

        imagePostfixIndex = 0;
        imageDetailActive = true;
        updateDetailImage(data);
        $('#DownloadImage').on('click', data, function (event) {
            imagePostfixIndex = 3;
            var link = document.createElement('a'); 
            var image_url = getBaseURL() + "/" + event.data.image_url + '.zip';
            //var image_url = siteURL + event.data.image_url + imagePostfix[imagePostfixIndex];
            //$('#TargetImg').attr("src",image_url);
            link.id = 'dnld_image';
            link.href = image_url;
            link.download = image_url;
            document.body.appendChild(link);
            link.click();
            $('#dnld_image').remove();

        });
        //$('#ShowRawImage').on('click', data, function (event) {
        //    var image_url = siteURL + event.data.image_url + "_rawcolor.jpg";
        //    $('#TargetImg').attr("src",image_url);
        //});
        $('#ShowImage').on('click', data, function (event) {
            imagePostfixIndex = 0;
            var image_url = getBaseURL() + "/" + event.data.image_url + imagePostfix[imagePostfixIndex];
            $('#TargetImg').attr("src",image_url);
        });
        //$('#ShowBinaryImage').on('click', data, function (event) {
        //    imagePostfixIndex = 1;
        //    var image_url = siteURL + event.data.image_url + imagePostfix[imagePostfixIndex];
        //    $('#TargetImg').attr("src",image_url);
        //});
        /*$('#ShowBoundaryImage').on('click', data, function (event) {
            imagePostfixIndex = 2;
            var image_url = siteURL + event.data.image_url + imagePostfix[imagePostfixIndex];
            $('#TargetImg').attr("src",image_url);
        });*/
        // Add event listener for window
        $(window).resize(debouncer (function() { return updateDetailImage(data);})); 
        //$(window).resize(function() { return updateDetailImage(data);});
        $('#ImageDetail').modal();
            
    };
   
    function buildPageNav(json) {
        // setup pages and buttons

        nextPage = json.image_data.next;
        previousPage = json.image_data.previous;

        totalImages = json.image_data.count;
        pageSize = json.page_size;

        if (totalImages % pageSize == 0) {
            totalPages = parseInt(totalImages/pageSize);
        }
        else {
            totalPages = parseInt(totalImages/pageSize) + 1;
        }
        if (totalPages > 1) {

            $('#page-container').empty();

            $('#page-container').append('<ul id="pages" class="pagination pagination-sm"></ul>');

            var currentPage = 1;
            if (nextPage != null) {
                currentPage = parseInt(nextPage.split('?page=')[1]) - 1;
            }     
            else if(previousPage != null) {
                currentPage = parseInt(previousPage.split('?page=')[1]) + 1;
                
            }
           
            var active = '';
            
            if (previousPage == null)
                $('#pages').append('<li class="disabled"><a href="#">Prev</a></li>');
            else
                $('#pages').append('<li><a href="#" onclick="rimsview.getPage(' + (currentPage-1) +')">Prev</a></li>');
            if (totalPages < 12) {
                for (var i=1;i <= totalPages;i++) {

                    lastSize = (i-1)*pageSize;
                    nextSize = i*pageSize-1;
                    if (nextSize > totalImages)
                        nextSize = totalImages;

                    if (currentPage == i) {
                            $('#pages').append(
                                    '<li class="active"><a href="#" onclick="rimsview.getPage(' + i +')">' + i + '</a></li>');
                        }
                        else {
                            $('#pages').append('<li><a href="#" onclick="rimsview.getPage('+i+')">' + i + '</a></li>');
                    }
                }
            }
            
            else {
            
                if (currentPage <= 4) {
                    for (var i=1;i <= 5;i++) {

                        lastSize = (i-1)*pageSize;
                        nextSize = i*pageSize-1;
                        if (nextSize > totalImages)
                            nextSize = totalImages;

                        if (currentPage == i) {
                            $('#pages').append(
                                    '<li class="active"><a href="#" onclick="rimsview.getPage(' + i +')">' + i + '</a></li>');
                        }
                        else {
                            $('#pages').append('<li><a href="#" onclick="rimsview.getPage('+i+')">' + i + '</a></li>');
                        }
                    }
                    $('#pages').append('<li class="disabled"><a href="#">...</a></li>');
                    $('#pages').append('<li><a  href="#" onclick="rimsview.getPage('+totalPages+')">' + totalPages + '</a></li>');
                }
                else if (currentPage >= totalPages - 3) {
                    $('#pages').append('<li><a  href="#" onclick="rimsview.getPage(1)">1</a></li>');
                    
                    $('#pages').append('<li class="disabled"><a href="#">...</a></li>');
                    
                    for (var i=totalPages-4;i <= totalPages;i++) {

                        lastSize = (i-1)*pageSize;
                        nextSize = i*pageSize-1;
                        if (nextSize > totalImages)
                            nextSize = totalImages;

                        if (currentPage == i) {
                            $('#pages').append(
                                    '<li class="active"><a href="#" onclick="rimsview.getPage(' + i +')">' + i + '</a></li>');
                        }
                        else {
                            $('#pages').append('<li><a href="#" onclick="rimsview.getPage('+i+')">' + i + '</a></li>');
                        }
                    }
                }
                else {
                    $('#pages').append('<li><a  href="#" onclick="rimsview.getPage(1)">1</a></li>');
                    
                    $('#pages').append('<li class="disabled"><a href="#">...</a></li>');
                    
                    for (var i=currentPage - 2;i <= currentPage + 2;i++) {

                        lastSize = (i-1)*pageSize;
                        nextSize = i*pageSize-1;
                        if (nextSize > totalImages)
                            nextSize = totalImages;

                        if (currentPage == i) {
                            $('#pages').append(
                                    '<li class="active"><a href="#" onclick="rimsview.getPage(' + i +')">' + i + '</a></li>');
                        }
                        else {
                            $('#pages').append('<li><a href="#" onclick="rimsview.getPage('+i+')">' + i + '</a></li>');
                        }
                    }


                    $('#pages').append('<li class="disabled"><a href="#">...</a></li>');
                    $('#pages').append('<li><a  href="#" onclick="rimsview.getPage('+totalPages+')">'+ totalPages +'</a></li>');

                } 

            }
            if (nextPage == null)
                $('#pages').append('<li class="disabled"><a href="#">Next</a></li>');
            else
                $('#pages').append('<li><a href="#" onclick="rimsview.getPage(' + (currentPage+1) +')">Next</a></li>');
            
        }
    };
    
    // Render mosaic using isotope
    function renderMosaicfromJSON(JSONData) {
       
        clearServerLoading();
        if (JSONData.image_data.results.length == 0) {
            statusBar.html("Found no matching images, please try different parameters.");
            return;
        }
        
        // Sort by image height
        JSONData.image_data.results = JSONData.image_data.results.sort( function (a,b) {
            return b.image_height - a.image_height;
        });
        
        for ( var i = 0; i < JSONData.image_data.results.length; i++ ) {
            var elem = getItemElement(JSONData.image_data.results[i]);
            mosaicContainer.append(elem);
        }

        // create item element for each image
        function getItemElement(data) {
            var elem = document.createElement('div');
            var img = new Image();
            img.src = getBaseURL()+ "/" + data.image_url+".jpg";
            img.onload = function() {
                loadedCounter++;
                elem.style.backgroundImage = "url('"+img.src+"')";
                var pct = Math.floor(100*loadedCounter/JSONData.image_data.results.length);
                statusBar.width(pct.toString()+"%");
                if (loadedCounter == JSONData.image_data.results.length) {
                    statusBar.html(renderQueryString(JSONData));
                }
                else {
                    statusBar.html("Loaded "+loadedCounter.toString()+" of "+JSONData.image_data.results.length.toString()+" images");
                }
            };
            elem.className = 'image-item'
            
            if (data.user_labels.length > 0) {
                elem.className += ' labeled-image-item';
            }
            
            elem.classTag = 'image-item'
            
            if (data.tags.length > 0) {
                elem.classTag += ' tagged-image-item';
            }
            
            elem.style.width = data.image_width.toString()+"px";
            elem.style.height = data.image_height.toString()+"px";
            elem.roi_data = data;
            return elem;
        };
        
        var cameraIndex = camera.val();
        var res = cameraRes[cameraIndex];
        
        // Delegate mouse enter event to image items 
        $('.image-item').on('mouseenter', function(){
            var data = this.roi_data;
            var majLen = data.major_axis_length.toString()*res;
            var minLen = data.minor_axis_length.toString()*res;
            var text = data.image_timestamp + ", Major Length: " + majLen.toPrecision(3) + " mm, Minor Length: " + minLen.toPrecision(3) + " mm";
            if (data.user_labels.length > 0) {
                text = text + ", Labels: ";
                for (var k = 0;k < data.user_labels.length;k++) {
                    if (k != 0)
                        text = text + ", ";
                    text = text + data.user_labels[k];
                }
            }
            
            if (data.tags.length > 0) {
                text = text + ", Tags: ";
                for (var k=0; k < data.tags.length; k++) {
                    if (k != 0)
                        text = text + ", ";
                    text = text + data.tags[k];
                }
            }
            
            statusText.html(text);
            
        });

        // Make images draggable (test)
        //$('.image-item').attr('draggable',true);
        
        // Delegate mouse click event to image items
        $('.image-item').on('click', function(e) {
            
            // If shift is pressed, just select the ROI
            if (e.altKey && isAuthenticated) {
                
                // mark the start time if no images have been
                // selected yet
                if ($('.selected-image-item').length == 0) {
                    d1 = new Date();
                    startedTime = d1.getTime();
                    //console.log(startedTime);
                }
                
                // Add selected class if not selected. 
                // otherwise removed selected
                if ($(this).hasClass('selected-image-item')) {
                    $(this).removeClass('selected-image-item');
                }
                else {
                    $(this).addClass('selected-image-item');
                }
                // print out selected
                //console.log($('.selected-image-item'));
                return;
            }
            
            // Otherwise show image detail
            showImageDetail(this.roi_data);
            
        });
    };
   
    
    // Public Methods
    var my = {};
    
    my.buildPresetMenu = function() {
    // build preset menu
        $.each(queryPresets, function(index,preset) {
            var li = $('<li/>')
                .addClass('ui-menu-item')
                .attr('data-toggle', 'tooltip')
                .prop('title',preset.title)
                .attr('data-placement','right')
                .appendTo($('#search-presets'));
            var a = $('<a/>')
                .addClass('ui-all')
                .attr('href', getBaseURL() + viewerBase + '?preset='+preset.name)
                .text(preset.label)
                .appendTo(li);
        });
    };
    
    my.loadPreset = function(params) {
        if (params['preset'] != undefined) {
        
            for (var i=0;i<queryPresets.length;i++) {
                
                if (queryPresets[i].name == params['preset']) {
                    preset = queryPresets[i];
                    minMaj.val(preset['minmaj'].toString());
                    maxMaj.val(preset['maxmaj'].toString());
                    minAspect.val(preset['minasp'].toString());
                    maxAspect.val(preset['maxasp'].toString());
                    camera.val(cameraNames.indexOf(preset['camera']).toString());
                    utcStart.val(preset['utcStart'].toString());
                    utcEnd.val(preset['utcEnd'].toString());
                }
            }
            //console.log(preset);
        }
    };

    my.returnToMainSite = function () {
        response = confirm('Leave viewer and return to main SPC site?');
        if (response) {
            window.open("http://spc.ucsd.edu","_self");
        }
    }

    my.invalidateData = function() {
        
        // This is a brute force way for now, but we 
        // only have a few fields to check. Net step,
        // use validator.js or similar for Bootstrap

        // Check all inputs and flag errors for user
        var allOkay = true;
        allOkay = checkIntInput(nImages,0,50000);
        //allOkay = checkIntInput(hourStart,0,24) == allOkay;
        //allOkay = checkIntInput(hourEnd,0,24) == allOkay;
        allOkay = checkFloatInput(minAspect,0,1) == allOkay;
        allOkay = checkFloatInput(maxAspect,0,1) == allOkay;
        allOkay = checkFloatInput(maxMaj,0,100) == allOkay;
        allOkay = checkFloatInput(minMaj,0,100) == allOkay;
        allOkay = checkFloatInput(maxDepth,0,1000) == allOkay;
        allOkay = checkFloatInput(minDepth,0,1000) == allOkay;
        allOkay = checkDatetimeInput(utcStart) == allOkay;
        allOkay = checkDatetimeInput(utcEnd) == allOkay;
        allOkay = checkDateRange(utcStart,utcEnd) == allOkay;
        allOkay = checkFloatRange(minMaj,maxMaj) == allOkay;
        allOkay = checkFloatRange(minAspect,maxAspect) == allOkay;
        allOkay = checkFloatRange(minDepth,maxDepth) == allOkay;
        //allOkay = checkFloatRange(hourStart,hourEnd) == allOkay;

        if (allOkay) {
            dataLoaded = false;
            runSearch.fadeOut(100,function(){
                runSearch.fadeIn(100);
            });
            //getArchive.fadeOut(100,function(){
            //    getArchive.fadeIn(100);
            //});
        }
        else {
            //$('.alert').show();
            //runSearch.fadeOut(800);
            //getArchive.fadeOut(800);
        }
    };
    
    my.loadDailyStats = function(cameraName) {
        $.ajax({
            url : dailyStatsBase + cameraName, // the endpoint
            type : "GET", // http method
            // handle a successful response
            success : function (json) {
                dailyStats[cameraNames.indexOf(cameraName)] = json.results;
                //dailyStats[dailyStatsIndex++] = json.results;
            },
        });
    };

    my.loadLabels = function() {
        $.ajax({
            url: getBaseURL() + '/rims-ptvr/rois/labels',
            type: 'GET',
            success: function (json) {
                allLabels = json['labels'];
               
                allLabels.sort(function(a,b) {
                    if (a.name > b.name)
                        return 1;
                    else if (a.name < b.name)
                        return -1;
                    else
                        return 0;
                });

                // get the name of the current selection
                var curSel = searchLabel.val();

                searchLabel.empty();
                searchLabel.append($('<option></option>').attr('value','Any').text('Any'));
                searchLabel.append($('<option></option>').attr('value','Unlabeled').text('Unlabeled'));
                for (var i = 0; i < allLabels.length;i++) {
                    searchLabel.append($("<option></option>").attr("value",allLabels[i].name).text(allLabels[i].name));
                }
                searchLabel.val(curSel).prop('selected',true);
                searchLabel.selectpicker('refresh');


                $('#label').typeahead('destroy');
                $('#label').typeahead({'source': allLabels});
            },
        });
    };
    
    my.getLabels = function() {
        return allLabels;
    };
    
    my.getLabelNames = function() {
        names = [];
        for (var i =0;i < allLabels.length;i++) {
            names.push(allLabels[i].name);
        }
        return names;
    };
    
    my.loadAnnotators = function() {
        $.ajax({
            url: getBaseURL() + '/rims-ptvr/rois/annotators',
            type: 'GET',
            success: function (json) {
                allAnnotators = json['annotators'];
               
                allAnnotators.sort(function(a,b) {
                    if (a.name > b.name)
                        return 1;
                    else if (a.name < b.name)
                        return -1;
                    else
                        return 0;
                });

                // get the name of the current selection
                var curSel = searchAnnotator.val();

                searchAnnotator.empty();
                searchAnnotator.append($('<option></option>').attr('value','Any').text('Any'));
                searchAnnotator.append($('<option></option>').attr('value','Unlabeled').text('Unlabeled'));
                for (var i = 0; i < allAnnotators.length;i++) {
                    searchAnnotator.append($("<option></option>").attr("value",allAnnotators[i].name).text(allAnnotators[i].name));
                }
                searchAnnotator.val(curSel).prop('selected',true);
                searchAnnotator.selectpicker('refresh');


                $('#label').typeahead('destroy');
                $('#label').typeahead({'source': allAnnotators});
            },
        });
    };
    
    my.getAnnotators = function() {
        return allAnnotators;
    };
    
    my.getAnnotatorNames = function() {
        names = [];
        for (var i =0;i < allAnnotators.length;i++) {
            names.push(allAnnotators[i].name);
        }
        return names;
    };


    
    my.loadTags = function() {
        $.ajax({
            url: getBaseURL() + '/rims-ptvr/rois/tags',
            type: 'GET',
            success: function (json) {
                allTags = json['tags'];
                allTags.sort(function(a,b) {
                    if (a.name > b.name)
                        return 1;
                    else if (a.name < b.name)
                        return -1;
                    else
                        return 0;
                });
                // get the name of the current selection
                
                var curSel = searchTag.val();

                searchTag.empty();
                searchTag.append($('<option></option>').attr('value','Any').text('Any'));
                searchTag.append($('<option></option>').attr('value','Untagged').text('Untagged'));
                for (var i = 0; i < allTags.length;i++) {
                    //console.log(allTags[i].name);
                    searchTag.append($("<option></option>").attr("value",allTags[i].name).text(allTags[i].name));
                }
                searchTag.val(curSel).prop('selected',true);
                searchTag.selectpicker("refresh");
                
                $('#tag').typeahead('destroy');
                $('#tag').typeahead({'source': allTags});
            },
        });
    };

    my.getTags = function() {
        return allTags;
    };
    
    my.getTagNames = function() {
        names = [];
        for (var i =0;i < allTags.length;i++) {
            names.push(allTags[i].name);
        }
        return names;
    };
    
    my.getDailyStats = function() {
        return dailyStats;
    };
    
    /*my.getArchiveData = function () {
    
        // Do nothing if data is already loaded
        if (dataLoaded)
            return;
            
        // Hide search button
        runSearch.hide();
        getArchive.hide();
        
        loadedCounter = 0;
       
        showServerLoading();
       
        var r = confirm("Are you sure you want to bundle and download the entire set of images matching these search parameters?");

        if (r == false) {
            runSearch.show();
            getArchive.show();

            return;

        }

        mosaicContainer.html(""); 
        $('#params').addClass('collapse');
        timeline.addClass('collapse');

        // get url of log file from python 
        log_url = buildArchiveURL();
        log_url = log_url.split("/").splice(6,12);
        log_url[1] = log_url[1].slice(0,log_url[1].length-3);
        log_url[2] = log_url[2].slice(0,log_url[2].length-3);
        log_url = 'http://spc.ucsd.edu/static/roistore/TMP/' + log_url.join("-") + '.json';

        var timer = 0;
        var logger = setInterval(
            function(){
                timer = timer + 0.5;
                //mosaicContainer.html('<blockquote><h4>'+timer.toString() + ' seconds</h4></blockquote>');
                $.ajax({
                    url: log_url,
                    type: "GET",
                    success: function (json) {
                        mosaicContainer.html('<blockquote><h4>'+timer.toString() + " seconds.<br/>" + json.join("<br/>")+'</h4></blockquote>');
                    }
                });
            },
            500
        );
        
        // Connect to server and get data
        $.ajax({
            url : buildArchiveURL(), // the endpoint
            type : "GET", // http method
            // handle a successful response
            success : function (json) {           
                clearInterval(logger);
                dataLoaded = true;
                if (json.archive_url.length != 0) {
                    var link = document.createElement("a")
                    link.download = json.archive_url.split("/").slice(-1)[0];
                    link.href = json.archive_url;
                    link.click();
                    mosaicContainer.html(mosaicContainer.html() + '<blockquote><h4> Data Available for 24 hours at http://spc.ucsd.edu/' + json.archive_url + '</h4></blockquote>');
                }   
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            }
        });
        
        // Clear containers
        //console.log("clearing containers...");
        clearContainers();
    };*/
    
    // Load data from the server using the current search settings
    my.loadRoiData = function() {
    
        // Do nothing if data is already loaded
        //if (dataLoaded)
        //    return;
            
        // Hide search button
        $('#page-container').empty();
        statusText.html('');
        runSearch.hide();
        //getArchive.hide();
        
        loadedCounter = 0;
       
        showServerLoading();
    
        lastQueryUrl = buildQueryURL(); 

        // Connect to server and get data
        $.ajax({
            url : lastQueryUrl, // the endpoint
            type : "GET", // http method
            // handle a successful response
            success : function (json) {           
                dataLoaded = true;
                if (json.archive_url.length != 0) {
                    var link = document.createElement("a")
                    link.download = json.archive_url.split("/").slice(-1)[0];
                    link.href = json.archive_url;
                    link.click();
                }   
                
                buildPageNav(json);
                
                renderMosaicfromJSON(json);
                

                
                runSearch.show();
                //getArchive.show();
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                //console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
        
        // Clear containers
        //console.log("clearing containers...");
        clearContainers();
    };
   
    my.getPage = function(pageNumber) {
    
        // Do nothing if data is already loaded
        //if (dataLoaded)
        //    return;
            
        // Hide search button
        statusText.html('');
        runSearch.hide();
        //getArchive.hide();
        
        loadedCounter = 0;
       
        showServerLoading(); 

        // Connect to server and get data
        $.ajax({
            url : lastQueryUrl + '?page=' + pageNumber, // the endpoint
            type : "GET", // http method
            // handle a successful response
            success : function (json) {           
                dataLoaded = true;
                buildPageNav(json);
                renderMosaicfromJSON(json);
                runSearch.show();
                //getArchive.show();
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                //console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
       


        // Clear containers
        //console.log("clearing containers...");
        clearContainers();
    };



    // Render timeline using highcharts
    my.renderTimeline = function() {
        var width= $("#timeline").width();
        // Prepare data
        
        dat = [];
        //console.log(dailyStats);
        for (var k=0;k<dailyStats.length;k++) {
            dat[k] = $.map(dailyStats[k],function (val,i) {
                if (val.total_rois == 0)
                    return [[Date.parse(val.day + " PST"),1]];
                else
                    return [[Date.parse(val.day + " PST"),val.total_rois]];
            });
            //console.log(dat[k]);
        }
        
        $('#timeline').highcharts({
            chart: {
                zoomType: 'x',
                backgroundColor: '#000000',
                plotBackgroundColor: '#000000',
                width: width,
                events: {
                            
                },
            },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            xAxis: {
                type: 'datetime',
                minRange: 14 * 24 * 3600000 // fourteen days
            },
            yAxis: {
                type: 'logarithmic',
                title: {
                    text: 'Counts'
                },
                min: 1000,
                tickInterval: 1,
            },
            legend: {
                enabled: true
            },
            tooltip: { 
                enabled: false 
            },
            plotOptions: {
                area: {
                    trackByArea: true,
                    events: {
                        click: function(e) {
                            updateSearchDateTime(e.point.x);
                            my.invalidateData();
                        }
                    }
                },
                series: {
                    point: {
                        events: {
                            mouseOver: function () {
                                updateDateTimeHover(this.x,this.y);
                            }
                        }
                    }
                }
            },
            
        });
        
        // Add any more series
        for (var i = 0; i< dat.length;i++) {
            //console.log(cameraNames[i]);
            $('#timeline').highcharts().addSeries({
                type: 'area',
                name: cameraNames[i],
                pointInterval: 24 * 3600*1000,
                pointStart: Date.UTC(2014, 2, 09),
                data: dat[i]
            });
        }
        
        // Add plotline with the current selected date
        $('#timeline').highcharts().xAxis[0].addPlotLine({
            value: Date.parse(utcStart.val()),
            width: 5,
            color: '#FFF',
            id: 'selected-line'
        });
    };
    
    my.labelSelectedImages = function(labelsAndTags) {
        prepAjax();
        //console.log(labelsAndTags);
        //console.log(JSON.stringify(labelsAndTags));
        $.ajax({
            //url: getBaseURL() + '/data/rois/label_images',
            url: siteURL + '/rims-ptvr/rois/label_images',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            processData: false,
            data: JSON.stringify(labelsAndTags),
            success: function(result) {
                //console.log(result);
                var label_counter = 0;
                var tag_counter = 0;
                // mark selected images as labeled or tagged from result
                sel = $('.selected-image-item');
                limgs = result['labeled_images'];
                timgs = result['tagged_images'];
                for (var i=0;i<sel.length;i++) {
                    if (limgs.indexOf(sel[i].roi_data.image_id) != -1) {
                        label_counter++;
                        $(sel[i]).addClass('labeled-image-item');
                    }
                    if (timgs.indexOf(sel[i].roi_data.image_id) != -1) {
                        tag_counter++;
                        $(sel[i]).addClass('tagged-image-item');
                    }
                }
                //Alert the result
                $('#label-result-text').html("Labeled " + label_counter + " and tagged " + tag_counter +
                        " images on the server.");
                $('#label-result').show();
                $('#label-result').fadeOut(5000);
                //clear selected images
                $('.selected-image-item').removeClass('selected-image-item');
                //$('.labeled-image-item').hide();
                //$('.tagged-image-item').hide();
                
                // Reload labels and tags incase new ones were added
                my.loadLabels();
                my.loadTags();
            },
        });
    };

    my.isAuthenticated = function () {
        return isAuthenaticated;
    };

    my.getUsername = function () {
        if (isAuthenaticated)
            return username;
        else
            return '';
    };

    
    my.checkAuth = function() {
        getUser();
    };

    // Get the labels and tags
    labels = my.getLabels();
    tags = my.getTags();

    // Check for Authenatication
    getUser();

    //Register callbacks
    timelineToggle.on( "click", function() {
        timeline.toggleClass('collapse');
        timeline.width('100%');
        my.renderTimeline();
        $(this).toggleClass('active');
    });
    
    
    searchParamsToggle.on( "click", function() {
        $('#params').toggleClass('collapse');
        $(this).toggleClass('active');
    });

    searchLabelParamsToggle.on( "click", function() {
        $('#label-params').toggleClass('collapse');
        $(this).toggleClass('active');
    });

    searchByName.on( "click", function() {
        $('#named-search').toggleClass('collapse');
        $(this).toggleClass('active');
    });
    
    runNamedSearch.on( "click", function() {
        // Check for value
        name = $('#name-to-search').val();
        if (name == '') {
            $('#name-to-search').val('Please enter a name to search');
            return;
        }
        $.ajax({
            url : getBaseURL() + "/data/rois/find_image/" + name, // the endpoint
            type : "GET", // http method
            // handle a successful response
            success : function (json) {           
                //console.log(json);
                if (json['image_id'] != '')
                    showImageDetail(json);
                //renderMosaicfromJSON(json);
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
            }
        });
        
    });

    
    runSearch.on( "click", my.loadRoiData);
    //getArchive.on( "click", my.getArchiveData);
  
    $('#select-all').on('click', function () {
        if ($('.selected-image-item').length == 0) {
            d1 = new Date();
            startedTime = d1.getTime();
            //console.log(startedTime);
        }
        $('.image-item').addClass('selected-image-item');
    });
    
    /*$('#hide-labeled').on('click',function() {
        if (hideLabeled.prop('checked') == true)
            $('.labeled-image-item').hide();
        else
            $('.labeled-image-item').show();
    });*/
    
    $('#clear-selected').on('click', function () {
        $('.image-item').removeClass('selected-image-item');
    });
    
    $('#invert-selected').on('click', function () {
        if ($('.selected-image-item').length == 0) {
            d1 = new Date();
            startedTime = d1.getTime();
            //console.log(startedTime);
        }
        $('.image-item').toggleClass('selected-image-item');
    });

    $('#submit-selected').on('click', function () {
        var labelsAndTags = {};
        labelsAndTags['label'] = $('#label').val();
        labelsAndTags['tag'] = $('#tag').val();
        //console.log($('#tag').val().split(", "));
        labelsAndTags['machine_name'] = $('#machine_name').val();
        labelsAndTags['is_machine'] = false;
        labelsAndTags['notes'] = $('#notes').val();
        labelsAndTags['user_info'] = '';
        labelsAndTags['query_path'] = lastQueryUrl;
        labelsAndTags['images'] = [];
        d1 = new Date();
        labelsAndTags['submitted'] = d1.getTime();
        labelsAndTags['started'] = startedTime; 


        if (labelsAndTags['label'] == 'None' & labelsAndTags['tag'] == 'None') {
            alert('No labels or tags to apply.');
            return;
        }

        sel = $('.selected-image-item');
        for (var i=0;i<sel.length;i++) {
            labelsAndTags['images'].push(sel[i].roi_data.image_id);
        }

        var proceed = confirm('Apply label: ' + labelsAndTags['label'] +
            ' and tag: ' + labelsAndTags['tag'] + ' to ' + sel.length +
            ' selected images?');

        //console.log(labelsAndTags);

        if (!proceed)
            return;

        // Apply the tags and labels
        //console.log(labelsAndTags);
        my.labelSelectedImages(labelsAndTags);
    
    });

    
    $('#ImageDetail').on('hide.bs.modal', function (e) {
        imageDetailActive = false;
        /*$('#ShowBoundaryImage').unbind();*/
        $('#ShowBinaryImage').unbind();
        $('#ShowImage').unbind();
        $('#ShowRawImage').unbind();
        $('#DownloadImage').unbind();
    });

    my.dailyStats = dailyStats;
    
    return my;
    
})();

// Get any parameters from URL
var urlParams;
(window.onpopstate = function () {
    var match,
        pl     = /\+/g,  // Regex for replacing addition symbol with a space
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
        query  = window.location.search.substring(1);

    urlParams = {};
    while (match = search.exec(query))
       urlParams[decode(match[1])] = decode(match[2]);
})();

rimsview.loadPreset(urlParams);


rimsview.buildPresetMenu();
// Load initial data
rimsview.loadLabels();
rimsview.loadAnnotators();
rimsview.loadTags();
rimsview.loadRoiData();

// Check for login
rimsview.checkAuth();

$(function() {
    $('[data-toggle="tooltip"]').tooltip()
})
