var iotdata = null;

function initAWS() {
    // Storing key/secret in local storage is for demo purposes only. Consider using AWS Cognito.
    var accessKeyId = window.localStorage.getItem("accessKeyId");
    var secretAccessKey = window.localStorage.getItem("secretAccessKey");
    var endpoint = window.localStorage.getItem("endpoint");

    if(accessKeyId == null || secretAccessKey == null || endpoint == null) {
        console.error("Setup not complete.");
        return false;
    }
    
    AWS.config.credentials = new AWS.Credentials({
        accessKeyId, secretAccessKey
    });

    AWS.config.region = 'eu-west-1';
    iotdata = new AWS.IotData({endpoint: endpoint});

    console.log("Setup AWS SDK.");
    return true;
}

function getDeviceShadow() {
    var thingName = window.localStorage.getItem('thingName');
    console.log("getThingShadow");
    return iotdata.getThingShadow({thingName}).promise()
        .then(function(response) {
            console.log("Got shadow.");
            var payload = JSON.parse(response.payload);
            return payload;
        });
}

function updateDeviceShadow(payload) {
    var thingName = window.localStorage.getItem('thingName');
    console.log("Updating device shadow...");
    return iotdata.updateThingShadow({thingName, payload: JSON.stringify(payload)}).promise()
        .then(function(response) {
            console.log("Update thing shadow accepted");
            var payload = JSON.parse(response.payload);
            return payload;
        });
}