"use strict";

if ((process.env.NODE_ENV === 'production') && Boolean(process.env.SENTRY_DSN)) {
    import('@sentry/browser').then((Sentry) => {
        window.Sentry = Sentry;
        Sentry.init({
            dsn: process.env.SENTRY_DSN,
            release: process.env.SOURCE_VERSION,
        });
        if (window.FPBASE.user !== undefined){
            Sentry.configureScope((scope) => {
              scope.setUser(window.FPBASE.user);
            });
        }
    });
}


// import "core-js/stable";
// import 'core-js/features/array';
// import "regenerator-runtime/runtime";

//import './js/my-polyfills.js';
import algoliasearch from 'algoliasearch'
window.algoliasearch = algoliasearch;
import autocomplete from 'autocomplete.js/dist/autocomplete.jquery.js'


import 'select2/dist/css/select2.css';
import 'select2-theme-bootstrap4/dist/select2-bootstrap.css';
import 'nouislider/distribute/nouislider.min.css';
import './css/style.scss';
import './css/nv.d3.css';

import 'bootstrap';

import 'select2/dist/js/select2.full.js';
import './js/my-fontawesome.js';
import './js/nv.d3.js';

import ProgressBar from 'progressbar.js';
window.ProgressBar = ProgressBar;

import './js/project.js';
import './js/search_logic.js';
import initAutocomplete from './js/algolia.js';
window.initAutocomplete = initAutocomplete;

import './js/protein_page.js';
import './js/favit.js';
import './js/jquery.formset.js';
import './js/onload.js';
import './js/microscope.js';
import './js/scope_report.js';

import LineageChart from './js/lineage.js'
window.LineageChart = LineageChart;

import initFRET from './js/fret.js';
window.initFRET = initFRET;

import initSpectra from './js/spectra/spectra.js';
window.initSpectra = initSpectra;

import FPPropChart from './js/ichart.js';
window.FPPropChart = FPPropChart;

import BlastApp from './js/blastapp/app.jsx'
window.FPblast = BlastApp;
