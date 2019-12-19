function elm(n) { return document.getElementById(n) };
function show(n) { return elm(n).style.display = 'block'; }
function hide(n) { return elm(n).style.display = 'none'; }

var uiStates = {
    'notLoggedIn': function() {
        hide('form_Main');
        show('form_Credentials');
        hide('error');
    },
    'loggedIn': function() {
        hide('loading');
        show('form_Main');
        hide('form_Credentials');
        hide('error');
        loadStations(STATIONS);
    },
    'accessDenied': function() {
        hide('form_Main');
        show('form_Credentials');
        show('error');
        elm('errorText').innerHTML = "Invalid credentials. Please check them and re-enter.";
    }
};

elm('b_SetCredentials').onclick = function(e) {
    setCredentials(elm('f_accessKeyInput').value, elm('f_secretInput').value);
    setEndpoint(elm('f_endpointInput').value);
    setThingName(elm('f_thingNameInput').value);
    elm('f_secretInput').value = "";
    init();
    return false;
};

elm('b_ClearCredentials').onclick = function(e) {
    clearCredentials();
    init();
    return false;
};

elm('b_UpdateDisplay').onclick = function(e) {
    show('loading');
    updateDeviceShadow({
        "state": {
            "desired": {
                "stage": "train-display-board",
                "data": {
                    "station_code": elm('f_StationSelect').value
                }
            }
        }
    }).then(function(response) {
        hide('loading');
        show('accepted');
        setTimeout(function() {
            hide('accepted')
        }, 3000);
    });
};

function loadStations(stations) {
    var stationSelect = elm('f_StationSelect');
    for(var i=0;i<stations.length;i++) {
        var opt = stations[i];
        var el = document.createElement("option");
        el.textContent = opt[1];
        el.value = opt[0];
        stationSelect.appendChild(el);
    }
}

function uiState(state) {
    hide('loading');
    uiStates[state]();
}

function setCredentials(accessKeyId, secretAccessKey) {
    window.localStorage.setItem('accessKeyId', accessKeyId);
    window.localStorage.setItem('secretAccessKey', secretAccessKey);
}

function clearCredentials() {
    window.localStorage.removeItem('accessKeyId');
    window.localStorage.removeItem('secretAccessKey');
}

function setEndpoint(endpoint) {
    window.localStorage.setItem('endpoint', endpoint);
}

function setThingName(thingName) {
    window.localStorage.setItem('thingName', thingName);
}

function init() {
    show('loading');
    var hasCredentials = initAWS();
    if(hasCredentials) {
        getDeviceShadow()
            .then(function(shadow) {
                uiState('loggedIn');
                try {
                    var stationCode = shadow.state.reported.data.station_code;
                    console.log("Selected station code: " + stationCode);
                    elm('f_StationSelect').value = stationCode;
                } catch(e) {
                    // Location not set in shadow, can ignore.
                }
            })
            .catch(function(error) {
                if(error.code === 'ForbiddenException') {
                    uiState('accessDenied');
                }
            })
    } else {
        // Credentials not set
        uiState('notLoggedIn');
    }
}