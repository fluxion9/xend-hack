let $meterButton = document.getElementById("meterButton");

//meter control
function meterState() {
    //api request sample
    let currentMeterState = false;
    // API STATE CHECK
    if (currentMeterState == true) {
    $meterButton.style.backgroundCColor = "green";
    $meterButton.textContent = "METERS ON";
    $meterButton.addEventListener("click", meterState);
    } else if (currentMeterState == false) {
    $meterButton.style.backgroundColor = "red";
    $meterButton.textContent = "METERS OFF";
    $meterButton.addEventListener("click", meterState);
    } else {
        //throw a server error
        // throw {
        //     message: "Server is not reachable",
        // };
        alert("server not available please reload this page or try again later");
    }

    //BUTTON TESTING
    //   $meterButton.style.backgroundColor = "red";
    //   $meterButton.textContent = "METERS OFF";
    //   $meterButton.addEventListener("click", meterState);
}
