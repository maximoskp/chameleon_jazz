
function send_request_get_response(url, return_function){
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", url, true);
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.send();
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
         var jsonObj = JSON.parse(xhttp.response);
         return_function( jsonObj );
      }
  };
}
