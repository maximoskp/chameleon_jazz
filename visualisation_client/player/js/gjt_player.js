const Http = new XMLHttpRequest();
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

function send_GJT_request(url){
  Http.open("GET", url);
  Http.send();

  var name = url.split('name=')[1].replace('&r=', '_r~').replace('&h=', '_h~') + '.csv'

  Http.onreadystatechange = (e) => {
    var jsonObj = JSON.parse( Http.responseText );
    // var jsonObj = Http.responseText;

    // console.log( 'jsonObj:', jsonObj );
    // console.log( 'keys', Object.keys( jsonObj ) );
    // console.log( 'name', name );
    // console.log('jsonObj[name]:', jsonObj[name]);

    // returning the array part
    play_array( jsonObj[name] )
    // return jsonObj[name]
  }
}

function play_note_for_instrument(a, tempo){
  console.log(' ======================================== ');
  console.log('instrument: ', a[0]);
  console.log('pitch: ', a[1]);
  console.log('duration: ', a[3]*(60.0/tempo));
  console.log('volume: ', a[4]/127.0);
}
function show_chord(a){
  console.log('CHORD: ', a[1]);
}

function play_array( a ){
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

