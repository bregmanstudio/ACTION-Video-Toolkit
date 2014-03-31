#include "ofMain.h"
#include "avfVideoPlayerApp.h"

//========================================================================
int main( int argc, char *argv[] ){
	ofSetupOpenGL(1920,1080,OF_WINDOW);			// <-------- setup the GL context

	// this kicks off the running of my app
	// can be OF_WINDOW or OF_FULLSCREEN
	// pass in width and height too:
	ofRunApp(new avfVideoPlayerApp());

}
