#pragma once

#include "ofMain.h"
#include "ofxOpenCv.h"
#include "pkmOpticalFlow.h"
//#include "ofxOsc.h"
#include "ofxAVFVideoPlayer.h"
#include <stdio.h>

using namespace cv;

class avfVideoPlayerApp : public ofBaseApp{

	public:
		void setup();
		void update();
		void draw();

		void keyPressed  (int key);
		void keyReleased(int key);
		void mouseMoved(int x, int y );
		void mouseDragged(int x, int y, int button);
		void mousePressed(int x, int y, int button);
		void mouseReleased(int x, int y, int button);
		void windowResized(int w, int h);
		void dragEvent(ofDragInfo dragInfo);
		void gotMessage(ofMessage msg);
    
        std::vector<ofxAVFVideoPlayer *> videoPlayers;
//        std::vector<ofVideoPlayer *> qtVideoPlayers;
        static const int N_VIDEO_PLAYERS = 1;

        ofxCvColorImage colorImg, flowColorImg;
        ofxCvGrayscaleImage grayImg, prevGrayImg;
        Mat flowImg;
        
        pkmOpticalFlow oflow;
        
        int width, height, pastmn, pastdev, counter, totalnumframes;
        
//        ofxOscSender sender;
    
        vector<float> mnDevVector, orientedVector;
    
        FILE *tvl1;
        string actionDir;
};
