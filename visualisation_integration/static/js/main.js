var audioManager = new AudioManager();
var metronome = new Metronome(audioManager);
// metronome.play();

function send_request_get_response(url, return_function){
  Http.open("GET", url);
  Http.send();
  Http.onreadystatechange = (e) => {
    var jsonObj = JSON.parse( Http.responseText );
    // var jsonObj = Http.responseText;
    return_function( jsonObj );
  }
}