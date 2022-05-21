var xhttp = new XMLHttpRequest();
// const url='https://jsonplaceholder.typicode.com/posts';
// const url = 'http://155.207.188.7:5000/songcsvcomplex?name=ALL_THE_THINGS_YOU_ARE&r=3&h=3'
// Http.open("GET", url);
// Http.send();

// Http.onreadystatechange = (e) => {
//   console.log(Http.responseText)
// }

// const url = 'http://155.207.188.7:5000/songcsvcomplex?name=ALL_THE_THINGS_YOU_ARE&r=3&h=3'
// Http.open("GET", url);
// Http.send();

// Http.onreadystatechange = (e) => {
//   console.log(Http.responseText)
// }

function dynamicallyLoadScript(url) {
  var script = document.createElement("script");  // create a script DOM node
  script.src = url;  // set its src to the provided URL

  document.head.appendChild(script);  // add it to the end of the head section of the page (could change 'head' to 'body' to add it to the end of the body section instead)
}

var drumsKeys;
var allChordSymbols = [];
var currentChordIdx = 0;

// load all drums
function load_all_drums(){
  console.log('load_all_drums 2');
  drumsKeys = player.loader.drumKeys();
  var drumInfo = [];
  for(var i=0; i<drumsKeys.length; i++){
    drumInfo.push( player.loader.drumInfo(i) );
    dynamicallyLoadScript( drumInfo[drumInfo.length-1].url );
  }
  console.log('drumInfo:', drumInfo);
}

function get_chords_from_array( a ){
  allChordSymbols = [];
  for(var i=0; i<a.length; i++){
    if (a[i][0] == 'Chord'){
      allChordSymbols.push(a[i][1]);
    }
  }
}

function send_GJT_play_request(url){

  xhttp.open("GET", url, true);
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.send();
  var name = url.split('name=')[1].replace('&r=', '_r~').replace('&h=', '_h~') + '.csv'
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
         //window.alert(xhttp.responseText);

         //console.log(xhttp.responseText);
         var jsonObj = JSON.parse(xhttp.response);
         //console.log(jsonObj);
         play_array( jsonObj[name] );
         playstop = !playstop;
     		 metronome.toolSendsPlayStop(playstop);
      }
  };

  // Http.open("GET", url);
  // Http.send();
  //
  // var name = url.split('name=')[1].replace('&r=', '_r~').replace('&h=', '_h~') + '.csv'
  //
  // Http.onreadystatechange = (e) => {
  //   var jsonObj = JSON.parse( Http.responseText );
  //   // var jsonObj = Http.responseText;
  //
  //   // console.log( 'jsonObj:', jsonObj );
  //   // console.log( 'keys', Object.keys( jsonObj ) );
  //   // console.log( 'name', name );
  //   // console.log('jsonObj[name]:', jsonObj[name]);
  //
  //   // returning the array part
  //   play_array( jsonObj[name] );
  //   playstop = !playstop;
	// 	metronome.toolSendsPlayStop(playstop);
  //   // return jsonObj[name]
  // }
}

function play_note_for_instrument(a, tempo){
  // console.log(' ======================================== ');
  // console.log('instrument: ', a[0]);
  // console.log('pitch: ', a[1]);
  // console.log('duration: ', a[3]*(60.0/tempo));
  // console.log('volume: ', a[4]/127.0);
  if (a[0] == 'Piano'){
    player.queueWaveTable(audioContext, audioContext.destination
      , _tone_0000_JCLive_sf2_file, 0, a[1], a[3]*(60.0/tempo), 0.8*a[4]/127.0);
  }else if(a[0] == 'Bass'){
    player.queueWaveTable(audioContext, audioContext.destination
      , _tone_0320_Aspirin_sf2_file, 0, a[1], a[3]*(60.0/tempo), a[4]/127.0);
  }else{
    var drum_variable =  '_drum_' + drumsKeys[player.loader.findDrum( a[1] )];
    // console.log('drum_variable:', drum_variable);
    player.queueWaveTable(audioContext, audioContext.destination
      , eval(drum_variable), 0, a[1], a[3]*(60.0/tempo), a[4]/127.0);
  }
}
function show_chord(a){
  // console.log('CHORD: ', a[1]);
  document.getElementById('chord').innerHTML = a[1];
  document.getElementById('chord').style.fontWeight = "900";
  document.getElementById('chord').style.fontSize = "21";
  if (currentChordIdx < allChordSymbols.length - 1){
    document.getElementById('chord1').innerHTML = '\t' + allChordSymbols[currentChordIdx+1];
  }
  if (currentChordIdx < allChordSymbols.length - 2){
    document.getElementById('chord2').innerHTML = '\t' + allChordSymbols[currentChordIdx+2];
  }
  if (currentChordIdx < allChordSymbols.length - 3){
    document.getElementById('chord3').innerHTML = '\t' + allChordSymbols[currentChordIdx+3];
  }
  currentChordIdx++;
}

function play_array( a ){
  get_chords_from_array( a );
  currentChordIdx = 0;
  var tempo = a[0][4];
  var starting_onset = a[0][3];
  metronome.setTempo(tempo);
  var i = 1;
  while (a[i][0] != 'Precount'){
    i++;
  }
  var t = a[i][2];
  console.log('a[i]: ', a[i]);
  document.addEventListener('beatTimeEvent', function (e){
    if ( i < a.length ){
      // console.log('t:', t);
      // console.log('e.metroBeatTimeStamp - starting_onset:', e.metroBeatTimeStamp - starting_onset);
      // console.log('i:', i);
      while ( t < e.metroBeatTimeStamp - starting_onset ){
        // console.log('3');
        if ( a[i][0] == 'Piano' || a[i][0] == 'Bass' || a[i][0] == 'Drums' || a[i][0] == 'Precount' || a[i][0] == 'Metro' ){
          // console.log('4');
          play_note_for_instrument(a[i], tempo);
          i++;
        }else if( a[i][0] == 'Chord' ){
          // console.log('5');
          show_chord(a[i]);
          i++;
        }else{
          // console.log('6');
          i++;
        }
        if ( i >= a.length ){
          break;
        }
        if ( a[i][0] == 'Piano' || a[i][0] == 'Bass' || a[i][0] == 'Drums' || a[i][0] == 'Precount' || a[i][0] == 'Metro' ){
          t = a[i][2];
        }else if( a[i][0] == 'Chord' ){
          t = a[i][3];
        }
      }
      // i++;
    }else{
      playstop = !playstop;
      metronome.toolSendsPlayStop(playstop);
    }
      // document.getElementById('beatTime').innerHTML = e.metroBeatTimeStamp;
      // VELENIS: ADD PLAYER HERE
      // e.metroBeatTimeStamp is called very frequently and it includes the
      // time that we need to trigger notes
      // CAUTION: metronome currently does not work for tempo changes.
      // TODO: we need to fix it
      // console.log( 'time: ', e.metroBeatTimeStamp - starting_onset );
  });
}
