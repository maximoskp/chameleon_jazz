window.AudioContext = window.AudioContext || window.webkitAudioContext;

class AudioManager{

	constructor(){
		this.audioContext = new AudioContext();
		// console.log('this.audioContext: ', this.audioContext);
		this.finalAudioOut = this.audioContext.destination;
		this.mainAudioOut = this.audioContext.createGain();
		this.dummyAudioOut = this.audioContext.createGain();
		this.mainAudioOut.connect(this.finalAudioOut);
	}

	receiveAudioFromNode(audioInNode){
		audioInNode.connect(this.mainAudioOut);
		// console.log("audioInNode--1". audioInNode);
		if(audioInNode.outNodes == null){
			audioInNode.outNodes = [];
		}
		audioInNode.outNodes.push(this.mainAudioOut);
		// console.log("audioInNode--2". audioInNode);
	}
	sendAudioToNode(audioOutNode){
		this.mainAudioOut.connect(audioOutNode);
		if(audioOutNode.inNodes == null){
			audioOutNode.inNodes = [];
		}
		audioOutNode.inNodes.push(audioOutNode);
	}
	unplugAudioNode(audioNode){
		audioNode.disconnect(this.mainAudioOut);
	}

	getCurrentTime(){
		// console.log('this.audioContext.state: ', this.audioContext.state);
		// console.log('this.audioContext.currentTime: ', this.audioContext.currentTime);
		return this.audioContext.currentTime;
	}

	playBuffer(buff){
		var source = this.audioContext.createBufferSource();
		source.buffer = buff;
		source.connect(this.mainAudioOut);
		source.start(0);
	}

}