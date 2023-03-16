var audioManager = new AudioManager();
var metronome = new Metronome(audioManager);
// metronome.play();
function readTextFile(file)
{
    var rawFile = new XMLHttpRequest();
    rawFile.open("GET", file, false);
    rawFile.onreadystatechange = function ()
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                var allText = rawFile.responseText;
                alert(allText);
                kern_string = allText;
            }
        }
    }
    // rawFile.send(null);
    rawFile.send();
}