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



let mid = document.getElementById("mid");
let stat = document.getElementById("stat");
let loc = document.getElementById("loc");
let bal = document.getElementById("bal");


function getParams() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        let params = JSON.parse(this.responseText);
        let id = "", sta = "", location="";
        for (let i=0; i<params.count; i++) {
          id += params.mid[i]
          id += "<br><br>";
          sta += params.is_active[i] ? "Active" : "Deactivated";
          sta += "<br><br>";
          location += params.address[i];
          location += "<br><br>";
        }
        mid.innerHTML = id;
        loc.innerHTML = location;
        stat.innerHTML = sta;
        bal.innerHTML = params.balance;
      }
    };
    xhttp.open("GET", "/api/get-params", true);
    xhttp.send();
  }

getParams();
setInterval(getParams, 1500);
