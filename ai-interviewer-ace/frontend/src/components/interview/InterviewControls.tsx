import React from 'react';
import { Mic, MicOff, Video, VideoOff, XCircle } from 'lucide-react';
import Button from '../common/Button';
import { useInterview } from '../../context/InterviewContext';
import { useNavigate } from 'react-router-dom';

interface InterviewControlsProps {
  onEndInterview: () => void;
}

const InterviewControls: React.FC<InterviewControlsProps> = ({ onEndInterview }) => {
  const { state, dispatch } = useInterview();
  const navigate = useNavigate();
  
  const toggleMic = () => {
    dispatch({ type: 'TOGGLE_MIC' });
  };
  
  const toggleCamera = () => {
    dispatch({ type: 'TOGGLE_CAMERA' });
  };
  
  const handleEndInterview = () => {
    onEndInterview();
  };
  
  return (
    <div className="flex items-center justify-between bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center space-x-4">
        <button
          className={`p-3 rounded-full ${
            state.isMicActive ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'
          } hover:opacity-80 transition-opacity`}
          onClick={toggleMic}
          title={state.isMicActive ? 'Mute microphone' : 'Unmute microphone'}
        >
          {state.isMicActive ? <Mic className="h-6 w-6" /> : <MicOff className="h-6 w-6" />}
        </button>
        
        <button
          className={`p-3 rounded-full ${
            state.isCameraActive ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'
          } hover:opacity-80 transition-opacity`}
          onClick={toggleCamera}
          title={state.isCameraActive ? 'Turn off camera' : 'Turn on camera'}
        >
          {state.isCameraActive ? <Video className="h-6 w-6" /> : <VideoOff className="h-6 w-6" />}
        </button>
      </div>
      
      <Button
        variant="danger"
        onClick={handleEndInterview}
        icon={XCircle}
      >
        End Interview
      </Button>
    </div>
  );
};

export default InterviewControls;