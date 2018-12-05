import { library, dom } from '@fortawesome/fontawesome-svg-core';
import {
    faBook,
    faCamera,
    faChartArea,
    faCheck,
    faClock,
    faCog,
    faDownload,
    faExchangeAlt,
    faExclamationCircle,
    faExclamationTriangle,
    faExternalLinkAlt,
    faEye,
    faFilter,
    faFlag,
    faHeart,
    faInfo,
    faInfoCircle,
    faLightbulb,
    faLink,
    faList,
    faMinusCircle,
    faPlus,
    faQuestionCircle,
    faQuoteLeft,
    faSearch,
    faShare,
    faShareSquare,
    faSpinner,
    faSun,
    faTable,
    faTimes,
    faTh,
    faThumbtack,
    faTimesCircle,
    faTrashAlt,
    faUpload,
    faWrench,
} from '@fortawesome/free-solid-svg-icons'; // ES Module "as" syntax
import { faHeart as farHeart, faEye as farEye, faFlag as farFlag, faKeyboard } from '@fortawesome/free-regular-svg-icons';
import { faTwitter, faGoogle } from '@fortawesome/free-brands-svg-icons';

library.add(
    faBook,
    faCamera,
    faChartArea,
    faCheck,
    faClock,
    faCog,
    faDownload,
    faExchangeAlt,
    faExclamationCircle,
    faExclamationTriangle,
    faExternalLinkAlt,
    faEye,
    faFilter,
    faFlag,
    faHeart,
    faInfo,
    faInfoCircle,
    faKeyboard,
    faLightbulb,
    faLink,
    faList,
    faMinusCircle,
    faPlus,
    faQuestionCircle,
    faQuoteLeft,
    faSearch,
    faShare,
    faShareSquare,
    faSpinner,
    faSun,
    faTable,
    faTimes,
    faTh,
    faThumbtack,
    faTimesCircle,
    faTrashAlt,
    faUpload,
    faWrench,

    farHeart,
    farEye,
    farFlag,

    faTwitter,
    faGoogle,
);

// Replace any existing <i> tags with <svg> and set up a MutationObserver to
// continue doing this as the DOM changes.
dom.watch();
