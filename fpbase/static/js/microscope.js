// to anyone reading this... I apologize for how crapy this code is...
// i intend to refactor the whole program... but this was one of those times
// where a bad foundation just kept going.  the program works relatively well,
// but it sure isn't pretty.

var chart;
var CONST = {
    category: {
        dye: 'd',
        protein: 'p',
        light: 'l',
        filter: 'f',
        camera: 'c',
    },
    stype: {
        ex: 'ex',
        abs: 'ab',
        em: 'em',
        twop: '2p',
        bp: 'bp',
        bpx: 'bx',
        bpm: 'bm',
        sp: 'sp',
        lp: 'lp',
        bs: 'bs',
        qe: 'qe',
        pd: 'pd',
    }
};
var data = [];
var localData = {};
var options = {
    showArea: true,
    minwave: 300,
    maxwave: 1000,
    startingBrush: [350, 800],
    autoscaleBrush: false,
    exNormWave: undefined,
    scale: 'linear',
    hide2p: true,
    scaleToEC: false,
    scaleToQY: false,
    oneAtaTime: true,
};
var userOptions = {
    oneAtaTime: {type: 'checkbox', msg: 'Uncheck other similar filters when selecting a filter'},
    showArea: {type: 'checkbox', msg: 'Fill area under curve'},
    autoscaleBrush: {type: 'checkbox', msg: 'Auto-rescale X-axis (using zoom above auto-disables this)'},
    hide2p: {type: 'checkbox', msg: 'Hide 2-photon spectra by default'},
    scaleToEC: {type: 'checkbox', msg: 'Scale excitation spectra to extinction coefficient (% of highest fluor)'},
    scaleToQY: {type: 'checkbox', msg: 'Scale emission spectra to quantum yield'},
};
var svg = d3.select('#spectra svg');


function getData(slug) {
    var dfd = $.Deferred();
    // download if not already downloaded
    if (!(slug in localData)) {
        $.getJSON("/spectra/" + slug)
            .done(function(d) {

                for (var n=0; n < d.spectra.length; n++) {
                    d.spectra[n] = padDataLimits(d.spectra[n]);
                    d.spectra[n].exNormed = 1;
                    if (d.spectra[n].type == CONST.stype.twop & options.hide2p) {
                        d.spectra[n].disabled = true;
                    } else if (d.spectra[n].type == CONST.stype.twop & !options.hide2p) {
                        d.spectra[n].disabled = false;
                    }
                    if (d.spectra[n].category == CONST.category.light | d.spectra[n].category == CONST.category.camera) {
                        d.spectra[n].gradient = true;
                    }
                }
                localData[slug] = d.spectra;
                dfd.resolve(localData[slug]);
            })
            .fail(function(d) {
                dfd.reject(d.status);
            });
    } else { // otherwise pull from local dict
        dfd.resolve(localData[slug]);
    }
    return dfd.promise();
}

function padDataLimits(d) {
    for (var i = d.minwave - 1; i >= options.minwave; i--) {
        d.values.unshift({ x: i, y: 0 });
    }
    for (var n = d.maxwave + 1; n <= Math.max(options.maxwave, 1000); n++) {
        d.values.push({ x: n, y: 0 });
    }
    return d;
}

function dataHasKey(key) {
    return $.grep(data, function(obj) { return obj.key == key; }).length > 0;
}

function dataHasSlug(slug) {
    return $.grep(data, function(obj) { return obj.slug == slug; }).length > 0;
}

function dataItemMatching(filter, d) {
    d = d || data;
    return d.filter(function(item) {
        for (var key in filter) {
            if (item[key] === undefined || item[key] != filter[key])
                return false;
        }
        return true;
    });
}

function asyncFunction(item) {
  itemsProcessed++;
  if(itemsProcessed === array.length) {
    callback();
  }
};

function mergeSpectra(concatslug) {
    var dfd = $.Deferred();
    // download if not already downloaded
    if (!(concatslug in localData)) {
        var sp = [];
        var slugs = concatslug.split('/')
        slugs.shift()

        var asyncFunction = function(s, onfinished) {
            if (s.startsWith('laser')) {
                if (localData.hasOwnProperty(s)) {
                    sp.push.apply(sp, localData[s])
                } else {
                    var F = customLaser(+s.replace('laser-', ''));
                    localData[s] = [F];
                    sp.push.apply(sp, localData[s])
                }
                onfinished()
            } else if (!s.startsWith('merged')){
                if (localData.hasOwnProperty(s)) {
                    sp.push.apply(sp, localData[s]);
                    onfinished();
                } else {
                    getData(s).then(function(){
                        sp.push.apply(sp, localData[s]);
                        onfinished();
                    });
                }
            }
        }
        var itemsProcessed = 0;
        slugs.forEach(function(s, ind, array) {
            asyncFunction(s, function(){
                itemsProcessed += 1;
                if(itemsProcessed === array.length) {
                    names = slugs.map(function(o) { return localData[o][0].key }).reduce(function(a, b){ return a + "+" + b })
                    localData[concatslug] = [{
                        key: names,
                        values: combineSpectra(sp),
                        area: true,
                        color: 'url(#wavecolor_gradient)',
                        classed: 'combined-light-ex'
                    }]
                    dfd.resolve(localData[concatslug])
                }
            })
        });
    } else { // otherwise pull from local dict
        dfd.resolve(localData[concatslug]);
    }
    return dfd.promise();
}

function addMerged(comboslug){
    return mergeSpectra(comboslug).then(function(d){
        data.push(d[0])
    })
}

function addItem(slug, subtype) {
    // add spectral data to array
    subtype = subtype || false;

    return getData(slug)
        .then(function(d) {
            for (var i = 0; i < d.length; i++) {
                if ((!subtype | (d[i].type == subtype)) & !dataHasKey(d[i].key)) {
                    data.push(JSON.parse(JSON.stringify(d[i]))); // make a copy of the object
                }
            }
        })
        .fail(function(d) {
            console.log('item not found: ' + slug);
        });

}

function removeSubtypes(subtype) {
    ix = $.map(data, function(obj, index) {
        if (obj.type == subtype) {
            return index;
        }
    });
    for (var i = ix.length - 1; i >= 0; i--)
        data.splice(ix[i], 1);
}

function removeItem(slug, subtype) {
    // optional subtype argument can be used to remove a specific type of spectrum
    // rather than the whole slug family
    subtype = subtype || false;

    ix = $.map(data, function(obj, index) {
        if (obj.slug == slug) {
            if (!subtype | (obj.type == subtype)) {
                return index;
            }
        }
    });
    for (var i = ix.length - 1; i >= 0; i--){
        data.splice(ix[i], 1);
    };
}


///// chart setup


function refreshChart() {
    chart.lines.duration(300);
    if (options.autoscaleBrush) {
        var smin = 10000;
        var smax = 0;
        for (var i = 0; i < data.length; i++) {
            if (!data[i].disabled) {
                smin = Math.min(data[i].minwave, smin);
                smax = Math.max(data[i].maxwave, smax);
            }
        }
        chart.brushExtent([smin, smax]);
    }

    scaleDataToOptions();
    excitationNormalization();
    //calculateEfficiency();
    chart.update();
    updateGlobalGradient();
    chart.lines.duration(0);
    if (options.scaleToQY || options. scaleToEC || options.exNormWave) {
        $("#y-zoom-slider").show();
        resizeYSlider();
    } else {
        $("#y-zoom-slider").hide();
    }
}


//// Scaling functions

function unscale_all(){
    options.exNormWave = undefined;
    options.scaleToQY = false;
    options.scaleToEC = false;
    $("#exnormRadioOFF").prop('checked', true);
    $('#scaleToQY_input').prop('checked',false)
    $('#scaleToEC_input').prop('checked',false)
    refreshChart();
}

function scale_data_up(filter){
    // scale data "up" according to the data.scalar value
    // filter can be .e.g. {type: 'ex'} to scale by ExtCoeff
    var maxScalar = Math.max.apply(null, data.map(function(e) { return e.scalar || 0; })) || 1;
    for (var n=0; n < data.length; n++){
        // only scale certain data by filter
        var skip = false;
        if(data[n].scaled || data[n].scalar === undefined){ skip = true; }
        for (var key in filter) {
            if (data[n][key] === undefined || data[n][key] != filter[key]){
                skip=true;
                break;
            }
        }

        if (!skip){
            var SCALE = data[n].scalar || 0.001;
            if (data[n].type == 'ex'){ SCALE /= maxScalar; }
            // do the scaling
            for (var i=0; i < data[n].values.length; i++){
                data[n].values[i].y = data[n].values[i].y * SCALE;
            }
            data[n].scaled = SCALE;
        }
    }
}

function scale_data_down(filter){
    for (var n=0; n < data.length; n++){
        // only scale certain data by filter
        var skip = false;
        for (var key in filter) {
            if (data[n][key] === undefined || data[n][key] != filter[key] || !Boolean(data[n].scaled)){
                skip=true;
                break;
            }
        }
        if (!skip){
            for (var i=0; i < data[n].values.length; i++){
                data[n].values[i].y = data[n].values[i].y / data[n].scaled;
            }
            data[n].scaled = false;
        }
    }
}


function excitationNormalization() {
    if (Boolean(options.exNormWave)){
        for (var n = 0; n < data.length; n++) {
            if (data[n].type =='em'){
                var exvals = dataItemMatching({slug: data[n].slug, type: 'ex'})[0].values;
                var targetScalar = dataItemMatching({x: options.exNormWave}, exvals)[0].y;
                targetScalar = Math.max(targetScalar, 0.0001); // so we don't clobber the values with zero
                var currentScalar = data[n].exNormed;
                if (currentScalar != targetScalar) {
                    var S = targetScalar / currentScalar;
                    data[n].values = data[n].values.map(function(item){ return {x: item.x, y: item.y * S}; });
                    data[n].exNormed = targetScalar;
                }
            }
        }
    } else {
        for (var n = 0; n < data.length; n++) {
            if (data[n].type =='em' && data[n].exNormed != 1) {
                data[n].values = data[n].values.map(function(item){ return {x: item.x, y: item.y / data[n].exNormed}; });
                data[n].exNormed = 1;
            }
        }
    }
}

function resizeYSlider(){
    try {
        var rect = $('#spectrasvg').find('.nv-focus').first().find('.nv-background>rect')
        var h = +rect.attr('height');
        //var t = Math.abs(rect.offset().top - $('#spectrasvg').offset().top);
        $('#y-zoom-slider').height( h * 0.88 );
    } catch(e) {

    }

}

function scaleDataToOptions(){
    if (options.scaleToEC){
        scale_data_up({type: 'ex'});
    } else {
        scale_data_down({type: 'ex'});
    }

    if (options.scaleToQY){
        scale_data_up({type: 'em'});
    }else{
        scale_data_down({type: 'em'});
    }
}

//// ON WINDOW LOAD
function getUrlParams( prop ) {
    var params = {};
    var search = decodeURIComponent( window.location.href.slice( window.location.href.indexOf( '?' ) + 1 ) );
    var definitions = search.split( '&' );

    definitions.forEach( function( val, key ) {
        var parts = val.split( '=', 2 );
        params[ parts[ 0 ] ] = parts[ 1 ];
    } );

    return ( prop && prop in params ) ? params[ prop ] : params;
}


$(function() {
    $('#y-zoom-slider').hide();
    //$('[data-toggle="popover"]').popover()

    $.each( userOptions, function( key, value ) {
        $('#options-form')
            .append($('<div>', {class: 'custom-control custom-checkbox mb-1 pb-1'})
            .append($('<input>', {type: value.type, class:'custom-control-input', checked: options[key]})
                .attr('id', key + '_input')
                .change(function(){
                    if (value.type == 'checkbox') {
                        options[key] = this.checked;
                    } else {
                        options[key] = this.value;
                    }

                    if (key === 'showArea'){
                        if (this.checked) {
                            $(".nv-groups").removeClass('area-hidden')
                        } else {
                            $(".nv-groups").addClass('area-hidden')
                        }
                    }
                    refreshChart();
                })
            )
            .append($('<label>', {for: key + '_input', class: 'custom-control-label'}).text(value.msg))
        )
    });

    //initialize chart
    nv.addGraph(function() {
        chart = nv.models.lineChart()
            .options({
                focusEnable: true,
                focusShowAxisX: false,
                noData: "Add spectra below ...",
                showLegend: true,
                showXAxis: true,
                showYAxis: true,
                duration: 300,
                useInteractiveGuideline: !window.mobilecheck(),
                clipEdge: true,
                margin: {
                    left: 40,
                    bottom: 15,
                },
                yDomain: [0, 1],
                //forceY: [0,1.04],
                //forceX: [350, 750],
            });
        chart.lines.duration(0);
        chart.brushExtent(options.startingBrush);
        chart.interactiveLayer.tooltip.valueFormatter(function(d, i) {
            if (d){
                return Math.round(d*1000)/10 + '%';
            } else {
                return '--';
            }
        })

        // chart sub-models (ie. xAxis, yAxis, etc) when accessed directly
        // return themselves, not the parent chart, so need to chain separately

        // chart.xAxis.axisLabel('Wavelength (nm)');

        chart.yAxis
            .axisLabel('Normalized Ex/Em/Transmission')
            .tickFormat(d3.format('1%'))
            .axisLabelDistance(25);

        svg.datum(data).call(chart);

        chart.focus.dispatch.on('brush', function() {
            updateGlobalGradient();
        });

        chart.dispatch.on('stateChange', function(e) {
            chart.update();
        });

        try {
          var slider = document.getElementById('y-zoom-slider');
          noUiSlider.create(slider, {
              start: [1], // 4 handles, starting at...
              behaviour: 'tap-drag', // Move handle on tap, bar is draggable
              orientation: 'vertical',
              direction: 'rtl',
              range: {min: 0.1, max: 1},
              format: {
                    to: function ( value ) {
                      return Math.round(value*100)/100;
                    },
                    from: function ( value ) {
                      return value;
                    }
                  }
          });

          // update filter settings when user changes slider
          slider.noUiSlider.on("update", function(){
              [m, n] = chart.yDomain();
              chart.yDomain([m, slider.noUiSlider.get()]);
              chart.update();
          });
        }
        catch(error) {
          //console.error(error);
          console.log('could not find noUiSlider')
        }


    });

    resizeYSlider();
    $( window ).resize(function() {
        chart.update();
        resizeYSlider();
    });


    urlParams = getUrlParams();
    if ('s' in urlParams){
        var arr = urlParams.s.toLowerCase().split(',');
        for (var i = 0; i < arr.length; i++){
            //var opts = slugOptions(arr[i]);
            var opts = false;
            if (Boolean(opts)){
                try{
                    // STILL BUGGY
                    if (i==0) {
                        $("#fluor-select").val(opts.slug).change();
                    }

                } catch(e) { console.log(e); }

            }
        }
    } else {

    }

    $(".scale-btns input").change(function() { setYscale(this.value); });

    $('#undo-scaling').click(function() {
        unscale_all();
    });

});


function setYscale(type) {
    //type can be log or linear
    chart.lines.duration(300);
    [m, n] = chart.yDomain()
    if (type == 'log') {
        options.scale = 'log';
        chart.yDomain([0.001, n]);
        chart.yScale(d3.scale.log());
        chart.yAxis.tickValues([0.01, 0.033, 0.1, 0.33, 1]);
        refreshChart();
    } else {
        options.scale = 'linear';
        chart.yDomain([0, n]);
        chart.yScale(d3.scale.linear());
        chart.yAxis.tickValues(d3.range(0, 1, 0.2));
        refreshChart();
    }
    chart.lines.duration(0);
}


/// Form Events



var focusedItem;
$("body").on('focus', '.fluor-selector, .select2', function(event) {
    // Store the current value on focus and on change
    focusedItem = $(this).closest('.row').find('.fluor-selector').val();
});

// main function when fluor-selector has been changed
$("body").on('change', '.fluor-selector', function(event) {
    var selector = this;
    var slug = $(this).val();
    var row = $(this).closest('.row');
    // if the item is already selected, cancel operation
    if (dataHasSlug(slug) && slug != focusedItem) {
        alert(localData[slug][0].key.replace(' em','').replace(' 2p','')
            .replace(' ex','')+ ' is already selected.');
        if (focusedItem){
            row.find('.fluor-selector').val(focusedItem).change();
        }else {
            row.find('.fluor-selector').val(0).change();
        }

        return;
    }

    // Remove the previous item fom the list
    removeItem(focusedItem);
    $(selector).siblings('.item-link').remove();

    // Add the new item to the data (unless it's blank)
    // then update the chart
    if (slug != null && slug != 0) {
        addItem(slug).then(function() {
            if (localData[slug][0].url) {
                $(selector)
                    .parent()
                    .append(
                        $('<div>', {class: 'input-group-append item-link', title: 'visit item page'})
                        .append(
                            $('<a>', {
                                'class': 'item-link',
                                'href': localData[slug][0].url,
                                'target': "_blank",
                            })
                            .append(
                                $('<button>', { 'class': 'btn btn-info', type: 'button'} ).html($("#linkSVG").html())
                            )
                        )
                    );
            }

            // if the slug has a two-2 item...
            if (localData[slug].map(function(e) { return e.type; }).indexOf(CONST.stype.twop) > -1) {
                // show the checkbox
                row.find('input.2pcheck').prop('disabled', false);
                // get the two photon item in the data
                item2p = dataItemMatching({ slug: slug, type: CONST.stype.twop })[0]; // assume only 1
                // if the 2p button was already checked... keep 2p enabled
                if (row.find('input.2pcheck')[0].checked) {
                    item2p.disabled = false;
                }
            } else {
                // if it doesn't have 2P data, hide the box...
                row.find('input.2pcheck').prop('disabled', true);
            }
            refreshChart();
        });
    } else {
        refreshChart();
    }

    focusedItem = slug;

});


$("body").on('click', '.remove-row', function(e) {
    var row = $(this).closest('.row');
    var rowslug = row.find('select').val();
    if (rowslug == 'custom_bp' || rowslug == 'custom_laser') {
        rowslug = row.attr('id');
    }
    row.remove();
    removeItem(rowslug);

    refreshChart();
    if ($('.fluor-row').length <= 1) {
        $("#toggle_alls").hide();
    }
});


/// Form Templates
function customLaser(wave) {
    return padDataLimits({
        slug: 'custom_laser',
        key: wave + ' laser',
        area: true,
        color: wave_to_color(wave),
        minwave: wave,
        maxwave: wave,
        values: [
            {x: wave, y: 1},
        ]
    })
}


function updateCustomLaser(wave) {
    var F = customLaser(+wave);
    localData['laser-'+wave] = [F];
    removeItem('custom_laser');
    data.push(F);
}


/// STYLES

// example:
// createGradient($('svg')[0],'MyGradient',[
//   {offset:'5%', 'stop-color':'#f60'},
//   {offset:'95%','stop-color':'#ff6'}
// ]);

COLORS = { 380: '#610061', 381: '#640066', 382: '#67006a', 383: '#6a006f', 384: '#6d0073', 385: '#6f0077', 386: '#72007c', 387: '#740080', 388: '#760084', 389: '#780088', 390: '#79008d', 391: '#7b0091', 392: '#7c0095', 393: '#7c0095', 394: '#7f009d', 395: '#8000a1', 396: '#8100a5', 397: '#8100a9', 398: '#8200ad', 399: '#8200b1', 400: '#8300b5', 401: '#8300b9', 402: '#8300bc', 403: '#8300c0', 404: '#8200c4', 405: '#8200c8', 406: '#8100cc', 407: '#8100cf', 408: '#8000d3', 409: '#7f00d7', 410: '#7e00db', 411: '#7c00de', 412: '#7b00e2', 413: '#7900e6', 414: '#7800e9', 415: '#7600ed', 416: '#7400f1', 417: '#7100f4', 418: '#6f00f8', 419: '#6d00fb', 420: '#6a00ff', 421: '#6600ff', 422: '#6100ff', 423: '#5d00ff', 424: '#5900ff', 425: '#5400ff', 426: '#5000ff', 427: '#4b00ff', 428: '#4600ff', 429: '#4200ff', 430: '#3d00ff', 431: '#3800ff', 432: '#3300ff', 433: '#2e00ff', 434: '#2800ff', 435: '#2300ff', 436: '#1d00ff', 437: '#1700ff', 438: '#1100ff', 439: '#0a00ff', 440: '#0000ff', 441: '#000bff', 442: '#0013ff', 443: '#001bff', 444: '#0022ff', 445: '#0028ff', 446: '#002fff', 447: '#0035ff', 448: '#003bff', 449: '#0041ff', 450: '#0046ff', 451: '#004cff', 452: '#0051ff', 453: '#0057ff', 454: '#005cff', 455: '#0061ff', 456: '#0066ff', 457: '#006cff', 458: '#0071ff', 459: '#0076ff', 460: '#007bff', 461: '#007fff', 462: '#0084ff', 463: '#0089ff', 464: '#008eff', 465: '#0092ff', 466: '#0097ff', 467: '#009cff', 468: '#00a0ff', 469: '#00a5ff', 470: '#00a9ff', 471: '#00aeff', 472: '#00b2ff', 473: '#00b7ff', 474: '#00bbff', 475: '#00c0ff', 476: '#00c4ff', 477: '#00c8ff', 478: '#00cdff', 479: '#00d1ff', 480: '#00d5ff', 481: '#00daff', 482: '#00deff', 483: '#00e2ff', 484: '#00e6ff', 485: '#00eaff', 486: '#00efff', 487: '#00f3ff', 488: '#00f7ff', 489: '#00fbff', 490: '#00ffff', 491: '#00fff5', 492: '#00ffea', 493: '#00ffe0', 494: '#00ffd5', 495: '#00ffcb', 496: '#00ffc0', 497: '#00ffb5', 498: '#00ffa9', 499: '#00ff9e', 500: '#00ff92', 501: '#00ff87', 502: '#00ff7b', 503: '#00ff6e', 504: '#00ff61', 505: '#00ff54', 506: '#00ff46', 507: '#00ff38', 508: '#00ff28', 509: '#00ff17', 510: '#00ff00', 511: '#09ff00', 512: '#0fff00', 513: '#15ff00', 514: '#1aff00', 515: '#1fff00', 516: '#24ff00', 517: '#28ff00', 518: '#2dff00', 519: '#31ff00', 520: '#36ff00', 521: '#3aff00', 522: '#3eff00', 523: '#42ff00', 524: '#46ff00', 525: '#4aff00', 526: '#4eff00', 527: '#52ff00', 528: '#56ff00', 529: '#5aff00', 530: '#5eff00', 531: '#61ff00', 532: '#65ff00', 533: '#69ff00', 534: '#6cff00', 535: '#70ff00', 536: '#73ff00', 537: '#77ff00', 538: '#7bff00', 539: '#7eff00', 540: '#81ff00', 541: '#85ff00', 542: '#88ff00', 543: '#8cff00', 544: '#8fff00', 545: '#92ff00', 546: '#96ff00', 547: '#99ff00', 548: '#9cff00', 549: '#a0ff00', 550: '#a3ff00', 551: '#a6ff00', 552: '#a9ff00', 553: '#adff00', 554: '#b0ff00', 555: '#b3ff00', 556: '#b6ff00', 557: '#b9ff00', 558: '#bdff00', 559: '#c0ff00', 560: '#c3ff00', 561: '#c6ff00', 562: '#c9ff00', 563: '#ccff00', 564: '#cfff00', 565: '#d2ff00', 566: '#d5ff00', 567: '#d8ff00', 568: '#dbff00', 569: '#deff00', 570: '#e1ff00', 571: '#e4ff00', 572: '#e7ff00', 573: '#eaff00', 574: '#edff00', 575: '#f0ff00', 576: '#f3ff00', 577: '#f6ff00', 578: '#f9ff00', 579: '#fcff00', 580: '#ffff00', 581: '#fffc00', 582: '#fff900', 583: '#fff600', 584: '#fff200', 585: '#ffef00', 586: '#ffec00', 587: '#ffe900', 588: '#ffe600', 589: '#ffe200', 590: '#ffdf00', 591: '#ffdc00', 592: '#ffd900', 593: '#ffd500', 594: '#ffd200', 595: '#ffcf00', 596: '#ffcb00', 597: '#ffc800', 598: '#ffc500', 599: '#ffc100', 600: '#ffbe00', 601: '#ffbb00', 602: '#ffb700', 603: '#ffb400', 604: '#ffb000', 605: '#ffad00', 606: '#ffa900', 607: '#ffa600', 608: '#ffa200', 609: '#ff9f00', 610: '#ff9b00', 611: '#ff9800', 612: '#ff9400', 613: '#ff9100', 614: '#ff8d00', 615: '#ff8900', 616: '#ff8600', 617: '#ff8200', 618: '#ff7e00', 619: '#ff7b00', 620: '#ff7700', 621: '#ff7300', 622: '#ff6f00', 623: '#ff6b00', 624: '#ff6700', 625: '#ff6300', 626: '#ff5f00', 627: '#ff5b00', 628: '#ff5700', 629: '#ff5300', 630: '#ff4f00', 631: '#ff4b00', 632: '#ff4600', 633: '#ff4200', 634: '#ff3e00', 635: '#ff3900', 636: '#ff3400', 637: '#ff3000', 638: '#ff2b00', 639: '#ff2600', 640: '#ff2100', 641: '#ff1b00', 642: '#ff1600', 643: '#ff1000', 644: '#ff0900', 645: '#ff0000', 646: '#ff0000', 647: '#ff0000', 648: '#ff0000', 649: '#ff0000', 650: '#ff0000', 651: '#ff0000', 652: '#ff0000', 653: '#ff0000', 654: '#ff0000', 655: '#ff0000', 656: '#ff0000', 657: '#ff0000', 658: '#ff0000', 659: '#ff0000', 660: '#ff0000', 661: '#ff0000', 662: '#ff0000', 663: '#ff0000', 664: '#ff0000', 665: '#ff0000', 666: '#ff0000', 667: '#ff0000', 668: '#ff0000', 669: '#ff0000', 670: '#ff0000', 671: '#ff0000', 672: '#ff0000', 673: '#ff0000', 674: '#ff0000', 675: '#ff0000', 676: '#ff0000', 677: '#ff0000', 678: '#ff0000', 679: '#ff0000', 680: '#ff0000', 681: '#ff0000', 682: '#ff0000', 683: '#ff0000', 684: '#ff0000', 685: '#ff0000', 686: '#ff0000', 687: '#ff0000', 688: '#ff0000', 689: '#ff0000', 690: '#ff0000', 691: '#ff0000', 692: '#ff0000', 693: '#ff0000', 694: '#ff0000', 695: '#ff0000', 696: '#ff0000', 697: '#ff0000', 698: '#ff0000', 699: '#ff0000', 700: '#ff0000', 701: '#fd0000', 702: '#fb0000', 703: '#fa0000', 704: '#f80000', 705: '#f60000', 706: '#f40000', 707: '#f20000', 708: '#f10000', 709: '#ef0000', 710: '#ed0000', 711: '#eb0000', 712: '#e90000', 713: '#e80000', 714: '#e60000', 715: '#e40000', 716: '#e20000', 717: '#e00000', 718: '#de0000', 719: '#dc0000', 720: '#db0000', 721: '#d90000', 722: '#d70000', 723: '#d50000', 724: '#d30000', 725: '#d10000', 726: '#cf0000', 727: '#ce0000', 728: '#cc0000', 729: '#ca0000', 730: '#c80000', 731: '#c60000', 732: '#c40000', 733: '#c20000', 734: '#c00000', 735: '#be0000', 736: '#bc0000', 737: '#ba0000', 738: '#b90000', 739: '#b70000', 740: '#b50000', 741: '#b30000', 742: '#b10000', 743: '#af0000', 744: '#ad0000', 745: '#ab0000', 746: '#a90000', 747: '#a70000', 748: '#a50000', 749: '#a30000', 750: '#a10000', 751: '#9f0000', 752: '#9d0000', 753: '#9b0000', 754: '#990000', 755: '#970000', 756: '#950000', 757: '#930000', 758: '#910000', 759: '#8f0000', 760: '#8d0000', 761: '#8a0000', 762: '#880000', 763: '#860000', 764: '#840000', 765: '#820000', 766: '#800000', 767: '#7e0000', 768: '#7c0000', 769: '#7a0000', 770: '#770000', 771: '#750000', 772: '#730000', 773: '#710000', 774: '#6f0000', 775: '#6d0000', 776: '#6a0000', 777: '#680000', 778: '#660000', 779: '#640000', 780: '#610000' }

function wave_to_color(wave) {
    wave = Math.round(wave)
    if (wave < 380) {
        return "#000061"
    } else if (wave > 780) {
        return '#610000'
    } else {
        return COLORS[wave]
    }
}


var chartsvg = $('#spectra svg')[0]
var chartsvgNS = chartsvg.namespaceURI;
var grad = document.createElementNS(chartsvgNS, 'linearGradient');
grad.setAttribute('id', 'wavecolor_gradient');
grad.setAttribute('class', 'svggradient');
var defs = chartsvg.querySelector('defs') || chartsvg.insertBefore(document.createElementNS(chartsvgNS, 'defs'), svg.firstChild);
defs.appendChild(grad);

function updateGlobalGradient() {
    $(grad).empty();
    var cmin = chart.xAxis.domain()[0];
    var cmax = chart.xAxis.domain()[1];
    var range = cmax - cmin;
    var stop;
    for (var w = cmin; w < cmax; w += 50) {
        stop = document.createElementNS(chartsvgNS, 'stop');
        stop.setAttribute('offset', Math.round(100 * (w - cmin) / range) + '%');
        stop.setAttribute('stop-color', wave_to_color(w));
        grad.appendChild(stop);
    }
    stop = document.createElementNS(chartsvgNS, 'stop');
    stop.setAttribute('offset', '100%');
    stop.setAttribute('stop-color', wave_to_color(cmax));
    grad.appendChild(stop);
}


//// EFFICIENCY CALCULATIONS

function spectral_product(ar1, ar2) {
    // calculate product of two spectra.values
    var output = [];
    var left = Math.max(ar1[0].x, ar2[0].x);
    var right = Math.min(ar1[ar1.length - 1].x, ar2[ar2.length - 1].x);
    var offsetA1 = left - ar1[0].x; // these assume monotonic increase w/ step = 1
    var offsetA2 = left - ar2[0].x; // these assume monotonic increase w/ step = 1

    for (var i = 0; i < right - left; i++) {
        output.push({ x: left + i, y: ar1[offsetA1 + i].y * ar2[offsetA2 + i].y });
    }
    return output;
}

function trapz(arr, min, max) {
    // approximate area under curve as series of trapezoids
    min = min || 300;
    max = max || 1000;
    var sum = 0;
    for (i = 0; i < arr.length - 1; i++) {
        if (arr[i].x > min) {
            var d = (arr[i].y + arr[i + 1].y) / 2;
            sum += d;
        }
        if (arr[i].x > max) {
            break;
        }
    }
    return sum;
}


$("body").on('mousedown', '.effbutton', function(e, i) {
    var iSpec = $(this).data('ispec');
    var iFilt = $(this).data('ifilt');
    var overl = $(this).data('ioverlap');

    disabledData = [];
    for (var d = 0; d < data.length; d++) {
        disabledData.push(data[d].disabled);
        if (!(d == iFilt | d == iSpec)) {
            data[d].disabled = true;
        }
    }
    data.push({
        key: 'Collection',
        values: overlaps[overl],
        color: 'black',
        area: true
    });
    chart.update();
});



$("body").on('mouseup', '.effbutton', function(e) {

    var iSpec = $(this).data('ispec');
    var iFilt = $(this).data('ifilt');
    var overl = $(this).data('ioverlap');

    data.splice(-1, 1);
    for (var d = 0; d < data.length; d++) {
        if (!(d == iFilt | d == iSpec)) {
            data[d].disabled = false;
        }
        data[d].disabled = disabledData[d];
    }

    //    chart.xDomain(getDomainLimits(data));
    refreshChart();
});


function invertData(values){
    var out = [];
    for (var i = 0; i < values.length; i++){
        out.push({x: values[i].x, y: 1 - values[i].y})
    }
    return out
}


function combineSpectra(pathlist){
    return pathlist.reduce(function(acc, cur) {
            if (acc){
                return spectral_product(acc, cur.values);
            } else {
                return cur.values;
            }
        }, null);
}

// disgusting awful code design
function calcExEmPaths(){
    var expath = $(".ex-filter:checked").map(function(){ return localData[this.value][0] }).get();
    var bspath = $(".bs-filter:checked").map(function(){ return localData[this.value][0] }).get();
    var empath = $(".em-filter:checked").map(function(){ return localData[this.value][0] }).get();
    var inverted = $(".invswitch:checked").map(function(){ return this.value }).get();

    for (var n=0; n < bspath.length; n++){
        var invVals = Object.assign({}, bspath[n]);
        invVals.values = invertData(bspath[n].values);
        if ($.inArray(bspath[n].slug , inverted) > -1 ){
            expath.push(bspath[n]);
            empath.push(invVals);
        } else {
            empath.push(bspath[n]);
            expath.push(invVals);
        }
    }

    if ($("#light-select :selected").val()){
        expath.push(localData[$("#light-select :selected").val()][0]);
    }

    if ($("#scale-camera").prop('checked')) {
        if ($("#camera-select :selected").val()){
            empath.push(localData[$("#camera-select :selected").val()][0]);
        }
    }


    return {exvalues: combineSpectra(expath), emvalues: combineSpectra(empath)}
}

function efficiency(filtervalues, fluor) {
    var dataitem = dataItemMatching(fluor)[0];
    if (!dataitem)
        return
    var fluorspectrum = dataitem.values;
    var filter_dye_spectrum = spectral_product(filtervalues, fluorspectrum);
    var filter_dye_area = trapz(filter_dye_spectrum);
    if (fluor.type == 'em'){
        var efficiency = filter_dye_area / trapz(fluorspectrum);
    } else if (fluor.type == 'ex'){
        var efficiency = filter_dye_area / trapz(filtervalues);
    }

    return {
        key: dataitem.key + ' eff',
        values: filter_dye_spectrum,
        efficiency: efficiency,
        area: true,
        color: "#333",
        classed: fluor.type + "-efficiency subtype-eff",
        type: 'eff',
        scalar: dataitem.scalar
    }
}



// KEYBINDINGS

function activateTab(tab){
  $('.nav-tabs a[href="#' + tab + '"]').tab('show');
};

function findEmptyOrAdd(table, formtype, subtype){
    focusedItem = 0;
    var el = $("#" + table + "-table").find('select option[value="0"]:selected');
    if(el.length){
        el.last().closest('select').select2('open');
    } else {
        addFormItem(formtype, subtype, true);
    }
}


$( "body" ).keypress(function( event ) {

    // no double-events
    if ($(':focus').hasClass('select2-search__field')){ return; }

    // ALL KEYS REQUIRE SHIFT
    if ( event.which == 80 ) { // p key
        activateTab("proteintab");
        findEmptyOrAdd("protein", 'p')
    } else if ( event.which == 68 ) {  // d key
        activateTab("proteintab")
        findEmptyOrAdd("dye", 'd')
    } else if ( event.which == 77 ) {  // m key
        activateTab("emtab")
        findEmptyOrAdd("emfilter", 'f', 'bm')
    } else if ( event.which == 88 ) {  // x key
        activateTab("extab")
        findEmptyOrAdd("exfilter", 'f', 'bx')
    } else if ( event.which == 67 ) {  // c key
        activateTab("emtab")
        findEmptyOrAdd("camqe", 'c', 'qe')
    } else if ( event.which == 76 ) {  // l key
        activateTab("extab")
        findEmptyOrAdd("light", 'l')
    } else if ( event.which == 79 ) {  // o key
        activateTab("optionstab")
    } else if ( event.which == 70 ) {  // f key
        activateTab("efftab")
    }

});

$( "body" ).keydown(function( event ) {
    if ( event.which == 8 ) { // delete key
        var nextobject = $(':focus').closest('.row').prev('.row').find('.select2-selection--single');
        $(':focus').closest('.input-group').find('button.remove-row').click();
        nextobject.focus();
    }
    if ( event.which == 38 ) { // up key
        event.preventDefault();
        $(':focus').closest('.row').prev('.row').find('.select2-selection--single').focus();
    }
    if ( event.which == 40 ) { // up key
        event.preventDefault();
        $(':focus').closest('.row').next('.row').find('.select2-selection--single').focus();
    }

    if ( event.which == 39 ) { // right key
        event.preventDefault();
        $(".nav-tabs .nav-link.active").closest('li.nav-item').next('.nav-item').find('.nav-link').click();
    }
    if ( event.which == 37 ) { // left key
        event.preventDefault();
        $(".nav-tabs .nav-link.active").closest('li.nav-item').prev('.nav-item').find('.nav-link').click();
    }

})


