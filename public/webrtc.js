
let pc = new RTCPeerConnection();
let ws;
let targetId;

let localVideo = document.getElementById("localVideo");
let remoteVideo = document.getElementById("remoteVideo");

navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
  stream.getTracks().forEach(track => pc.addTrack(track, stream));
  localVideo.srcObject = stream;
});

pc.ontrack = event => {
  remoteVideo.srcObject = event.streams[0];
};

pc.onicecandidate = event => {
  if (event.candidate) {
    sendMessage({ type: "ice", candidate: event.candidate });
  }
};

function sendMessage(message) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ to: targetId, data: message }));
  }
}

function startCall() {
  targetId = document.getElementById("targetId").value;
  ws = new WebSocket(`ws://${location.host}/ws/${uid}`);

  ws.onmessage = async ({ data }) => {
    const msg = JSON.parse(data);
    const from = msg.from;
    const content = msg.data;

    if (content.type === "offer") {
      await pc.setRemoteDescription(new RTCSessionDescription(content));
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      ws.send(JSON.stringify({ to: from, data: answer }));
    } else if (content.type === "answer") {
      await pc.setRemoteDescription(new RTCSessionDescription(content));
    } else if (content.type === "ice") {
      await pc.addIceCandidate(new RTCIceCandidate(content.candidate));
    }
  };

  ws.onopen = async () => {
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    sendMessage(offer);
  };
}
