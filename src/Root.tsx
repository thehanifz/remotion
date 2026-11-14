import React from 'react';
import {Composition} from 'remotion';
import {CarrickVideo, TOTAL_FRAMES, FPS} from './CarrickVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="CarrickVideo"
        component={CarrickVideo}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
      />
    </>
  );
};
