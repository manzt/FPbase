var chart;
var data = [];
var localData = {};
var svg = d3.select('#spectra svg');
var donorEM;
var acceptorEX;
var options = {
    showArea: true,
    minwave: 350,
    maxwave: 750,
    startingBrush: [350, 750],
    autoscaleBrush: false,
    exNormWave: undefined,
    scale: 'linear',
    hide2p: true,
    scaleToEC: false,
    scaleToQY: false,
};

//initialize chart
nv.addGraph(function() {
    chart = nv.models.lineChart()
        .options({
            focusEnable: false,
            focusShowAxisX: false,
            noData: "Choose an acceptor and donor below",
            showLegend: true,
            showXAxis: true,
            showYAxis: true,
            duration: 300,
            useInteractiveGuideline: !window.mobilecheck(),
            clipEdge: true,
            margin: {
                left: 40,
                bottom: 55,
            },
            yDomain: [0, 1],
            xDomain: [350, 750],
            //forceY: [0,1.04],
            forceX: [350, 750],
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

    chart.xAxis.axisLabel('Wavelength (nm)');

    chart.yAxis
        .axisLabel('Normalized Ex/Em/Transmission')
        .tickFormat(d3.format('1%'))
        .axisLabelDistance(25);
    svg.datum(data).call(chart);
    chart.dispatch.on('stateChange', function(e) {
        chart.update();
    });

    nv.utils.windowResize(function(){ chart.update(); });
});

$("#donor-select").select2({ theme: "bootstrap", width: 100});
$("#acceptor-select").select2({ theme: "bootstrap", width: 100});

d3.selection.prototype.moveToFront = function() {
    return this.each(function() {
        this.parentNode.appendChild(this);
    });
};
d3.selection.prototype.moveToBack = function() {
    return this.each(function() {
        var firstChild = this.parentNode.firstChild;
        if (firstChild) {
            this.parentNode.insertBefore(this, firstChild);
        }
    });
};


function getData(slug) {
    var dfd = $.Deferred();
    // download if not already downloaded
    if (!(slug in localData)) {
        $.getJSON('/spectra/' + slug)
            .done(function(d) {
                for (var n = 0; n < d.spectra.length; n++) {
                    if (d.spectra[n].type !== '2p' ) {
                      d.spectra[n] = padDataLimits(d.spectra[n]);
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

function addItem(slug, subtype) {
    if (slug === '') {
      return $.Deferred(function(def) { def.resolve(); }).promise();
    }
    // add spectral data to array
    subtype = subtype || false;

    return getData(slug)
        .then(function(d) {
            for (var i = 0; i < d.length; i++) {
                if (d[i].type !== '2p' & !dataHasKey(d[i].key)) {
                    data.push(JSON.parse(JSON.stringify(d[i]))); // make a copy of the object
                }
            }
        })
        .fail(function(d) {
            console.log('item not found');
        });

}

function spectral_product(ar1, ar2) {
    // calculate product of two spectra.values
    var output = [];
    var step = ar1[1].x - ar1[0].x;
    var left = Math.max(ar1[0].x, ar2[0].x);
    var right = Math.min(ar1[ar1.length - 1].x, ar2[ar2.length - 1].x);

    var a1 = ar1.slice(ar1.findIndex(i => i.x === left), ar1.findIndex(i => i.x === right));
    var a2 = ar2.slice(ar2.findIndex(i => i.x === left), ar2.findIndex(i => i.x === right));
    for (var i = 0; i < a1.length; i++) {
        output.push({ x: a1[i].x, y: a1[i].y * a2[i].y });
    }


    return output;
}


function forster_distance(ar1, ar2, k2, ni){
  k2 = k2 || 2/3;
  ni = ni || 1.33;

  var donorQY = ar1.scalar;
  var accECmax = ar2.scalar;
  var a1wavemap = ar1.values.reduce(function(acc, cur){ acc[cur.x] = cur.y; return acc}, {});
  var a2wavemap = ar2.values.reduce(function(acc, cur){ acc[cur.x] = cur.y; return acc}, {})
  var donorsum = ar1.values.reduce(function(a,b){ return a + b.y},0);
  var startingwave = Math.max(ar1.minwave, ar2.minwave);
  var endingwave = Math.min(ar1.maxwave, ar2.maxwave);
  var step = ar1.values[1].x - ar1.values[0].x;
  var overlapIntgrl = 0;
  for (var wave = startingwave; wave <= endingwave; wave += step){
    overlapIntgrl += Math.pow(wave * 1e-7, 4) * a1wavemap[wave] * accECmax * a2wavemap[wave] / donorsum;
  }
  r = Math.pow(8.8 * 1e-25 * k2 * donorQY * Math.pow(ni, -4) * overlapIntgrl, 1/6) * 1e7;
  return [overlapIntgrl, r];
}


$('#ni-input').on('change', function() {
    var input=$(this);
    var val=input.val();
    input.val(Math.max(Math.min(val, 1.6), 0.5))
    updateTable();
});

$('#k2-input').on('change', function() {
    var input=$(this);
    var val=input.val();
    input.val(Math.max(Math.min(val, 4), 0))
    updateTable();
});

function updateTable(){
  try {
    var r = forster_distance(donorEM, acceptorEX, $('#k2-input').val(), $('#ni-input').val());
    $("#overlapIntgrl").text(Math.round(r[0] * 1e15) / 100);
    $("#r0").text(Math.round(r[1] * 1000) / 100);
  } catch(e) {
  }
}

// main function when data-selector has been changed
$(".data-selector").change(function(event) {
    data.splice(0, 10);
    var donorslug = $("#donor-select :selected").val();
    var acceptorslug = $("#acceptor-select :selected").val()
    $.when(addItem(donorslug), addItem(acceptorslug)).then(function(){
      if (donorslug || acceptorslug) {
        $('.table-wrapper').show()
      }
      if (donorslug){
        donorEM = dataItemMatching({slug: donorslug, type:'em'})[0];
        donorEM.classed += ' faded-fret';
        $("#QYD").text(donorEM.scalar);
      } else {
        $("#QYD").text('');
      }
      if (acceptorslug){
        acceptorEX = dataItemMatching({slug: acceptorslug, type:'ex'})[0];
        acceptorEX.classed += ' faded-fret';
        $("#ECA").text(acceptorEX.scalar.toLocaleString());
        $("#QYA").text(dataItemMatching({slug: acceptorslug, type:'em'})[0].scalar);
      } else {
        $("#ECA, #QYA").text('')
      }
      if (donorslug && acceptorslug) {
        data.push({
            key: 'Overlap',
            values: spectral_product(donorEM.values, acceptorEX.values),
            area: true,
            color: 'url(#diagonal-stripe-r)',
            classed: "fret-overlap",
            type: 'overlap',
        })
        updateTable(donorEM, acceptorEX);
      } else {
        $("#overlapIntgrl, #r0").text('')
      }
      chart.update();
      d3.selectAll(".faded-fret").moveToBack();
      d3.selectAll(".fret-overlap").moveToFront();
    })

});

$('body').on('click', '.load-button', function(){
  var donorslug = $(this).closest('tr').find('td:nth-child(2) a').attr('href').split('/')[2] + '_default'
  var accslug = $(this).closest('tr').find('td:nth-child(3) a').attr('href').split('/')[2] + '_default'
  $("#donor-select").val(donorslug).trigger('change.select2');
  $("#acceptor-select").val(accslug).change();

})

$(document).ready(function() {
    $('#fret_report').DataTable( {
        "ajax": "/fret/",
        "pageLength": 25,
        "order": [[9, 'desc']],
        "responsive": true,
        "language": {
          "emptyTable": "No Data received from server...",
          "loadingRecords": "Calculating FRET efficiencies across database...  Please wait."
        },
        "update": function ()
        {
            this._positions();
            this._scroll( false );
        },
        "columns": [
            { "data": function () { return '<button class="btn btn-sm btn-outline bg-transparent load-button"><i class="far fa-eye text-secondary"></i> </button>'},
              "responsivePriority": 2,
              "width": '1px',
              "orderable": false},
            { "data": "donor",
              "responsivePriority": 1,
              "width": '20px'},
            { "data": "acceptor",
              "responsivePriority": 1,
              "width": '20px'},
            { "data": "donorPeak",
              "responsivePriority": 4,
              "width": '10px'},
            { "data": "acceptorPeak",
              "responsivePriority": 4,
              "width": '10px'},
            { "data": "donorQY",
              "responsivePriority": 3},
            { "data": "acceptorEC",
              "responsivePriority": 3},
            { "data": "acceptorQY",
              "responsivePriority": 6},
            { "data": "overlap",
              "responsivePriority": 3},
            { "data": "forster",
              "responsivePriority": 1}
        ],
    } );
} );

var topofDiv = $(".spectra-wrapper").offset().top;
$(window).scroll(function(){
    if($(window).scrollTop() > (topofDiv)){
      $(".spectra-wrapper").css('box-shadow', '0 12px 8px -8px rgba(0,0,0,.2)');
    }
    else{
      $(".spectra-wrapper").css('box-shadow', 'none');
    }
});
