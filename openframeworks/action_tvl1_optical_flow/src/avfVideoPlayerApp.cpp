#include "avfVideoPlayerApp.h"


#define GRID_MULT 1
#define GRID_DIVS 8

#define HOST "localhost"
#define PORT 57000

// flags for internals debugging
#define _GUI                1 // show the generated window
// and the various sub-views:
#define _GUI_COLOR_IMG      0 //    - video direct image, unprocessed
#define _GUI_MOTION_IMG     0 //    - motion gradients, Parag's viewer with gutters
#define _GUI_mndev_HIST     0 //    - mean-dev,  bins (binned version of Parag's 360-degree visualizer, set this to 360 to see an approximation of that)
#define _GUI_SPAT_HIST      0 //    - my spatial histogram view (8-by-8 grid of cells, ranging from blue - yellowish

#define _LOG 1


//--------------------------------------------------------------
void avfVideoPlayerApp::setup(){


    actionDir = "/Users/kfl/Movies/action/";
//    actionDir = "/Volumes/ACTION/";
//    actionDir = "/Users/tomstoll/Movies/action/";

    
    // First read the list of Movie strings
    string titlesString;
    ofBuffer buffer = ofBufferFromFile(actionDir+"action_list.txt");
    
    titlesString = buffer.getText();
    
    buffer.clear();
    
    vector<string> allTitles = ofSplitString(titlesString, "\n");
    cout << titlesString << endl;
    cout << allTitles.size() << endl;

//    ofDirectory dir = ofDirectory(actionDir);
//    dir.listDir();
//    ofLogWarning("num. files: " + ofToString(dir.numFiles()));

    string found_tvl = "";
    string found_mov = "";
    int found_flag = 0;
    
    //go through all the paths and find the first one where .tvl1 does not exist
    for(int i = 0; i < allTitles.size(); ++i){
        
        if(found_flag<1) {
            string title = allTitles[i];
            cout << title << endl;
            string full_tvl_path = (actionDir + title + "/" + title + ".tvl1");
            cout << full_tvl_path << endl;
            string full_mov_path =(actionDir + title + "/" + title + ".mov");
            cout << full_mov_path << endl;
            ofFile tvl_file = ofFile(full_tvl_path);
            ofFile mov = ofFile(full_mov_path);
            
            cout << tvl_file.exists() << endl;
            cout << mov.exists() << endl;

            if ((tvl_file.exists()==0) && (mov.exists()==1)) {

                found_tvl = full_tvl_path;
                found_mov = full_mov_path;
                found_flag = 1;
                ofFile out;
                out.open(actionDir+"tvl1_log.txt", ofFile::Append, false);
                out << "Starting analysis of: " << title << "\n";
                out.close();
            }
        } else {
            break;
        }
    }
    
    ofFile out;
    out.open(actionDir+"tvl1_log.txt", ofFile::Append, false);
    out << "FF: " << found_flag << endl;
    out << found_tvl << endl;
    out << found_mov << endl;
    out.close();
    
    videoPlayers.push_back(new ofxAVFVideoPlayer());
    videoPlayers[0]->loadMovie(found_mov);
    videoPlayers[0]->setVolume(0);
    
//    qtVideoPlayers.push_back(new ofVideoPlayer());
//    qtVideoPlayers[0]->loadMovie(found_mov);
//    qtVideoPlayers[0]->setVolume(0);

    
    
//    for(int i=0; i<N_VIDEO_PLAYERS; i++) {
//        videoPlayers.push_back(new ofxAVFVideoPlayer());
//        videoPlayers[i]->loadMovie("/Volumes/ACTION/Vertigo/Vertigo.mov");
//    }
    width           = 320;
    height          = 240;
    counter         = 0;
    totalnumframes  = 0;
    
    //    ofSetFrameRate(60);
    ofSetWindowShape(width, height*4);
    ofSetVerticalSync(true);
    ofBackground(0);

    colorImg.allocate(width, height);
    //    flowColorImg.allocate(width, height);
    
    oflow = pkmOpticalFlow();
    oflow.allocate(width, height);
    
    mnDevVector = vector<float>((GRID_DIVS*GRID_DIVS*2),0.f);
    orientedVector = vector<float>(16,0.f);

    // header?
    // from here?:
    // http://forum.openframeworks.cc/t/getting-to-know-ofbuffer-saving-complex-data-types/7240/2
    tvl1 = fopen(found_tvl.c_str(),"wb");
    cout << "Done broke." << endl;

//    ofExit();
    
}

//--------------------------------------------------------------
void avfVideoPlayerApp::update(){
    int t=0;
    for(auto p : videoPlayers) {
//    for(auto p : qtVideoPlayers) {
        p->update();
        if(true || p->isLoaded()) {
            if(ofGetElapsedTimef() > t++ * 0.005)
                p->play();
            
                totalnumframes = p->getTotalNumFrames();
            cout << "dur: " << p->getDuration() << endl;
            cout << "tnf: " << totalnumframes << endl;
            cout << "et: " << ofGetElapsedTimef << endl;
            cout << p->getCurrentFrame() << endl;
        }
        
        ofPixelsRef ref = videoPlayers[0]->getPixelsRef();
//        ofPixelsRef ref = qtVideoPlayers[0]->getPixelsRef();
        colorImg.setFromPixels(ref);
        oflow.update(ref);
        
        cv::Mat oriented = oflow.computeHistogramOfOrientedMotionGradients(true);
        
        int grid_w = (int)256.f/GRID_DIVS;
        int grid_h = (int)192.f/GRID_DIVS;
        float mn = 0;
        float dev = 0;
        float x=0;
        int height = oriented.size().height;
        
//        cout << "height: " << height << endl;
        
        // iterate over vector, getting the binned value of the overall angles histogram
        // @ each histogram value:
        //  - store to the appropriate <float> Vector
        //  - fwrite a single float for each calculated val @ HIST_BINS per frame
        
        for (int i=0; i<height; i++) {
            x = oriented.at<float>(i);
            orientedVector[i] = x;              // FOR VISUALIZATION and fwrite
//          [aweg;ohu awecout << x << endl;
            fwrite( &x, 1, sizeof(x), tvl1 ) ;
        }
        
        // iterate over *square* matrix, getting the mean and st dev. for each grid square
        // @ each grid square:
        //  - store to the appropriate <float> Vector
        //  - fwrite a single float for each calculated val @ (GRID_DIVS * GRID_DIVS * 2) = GRIDDED_BINS per frame
        
        float sanity = 0.f;
        
        for (int y=0; y<GRID_DIVS; y++) {
            for (int x=0; x<GRID_DIVS; x++) {
                
                mn = oflow.getFlowMeanForROI((x*grid_w), (y*grid_h), grid_w, grid_h);
                dev = oflow.getFlowDevForROI((x*grid_w), (y*grid_h), grid_w, grid_h);
                
                mnDevVector[(((y*GRID_DIVS)+x)*2)] = mn;
                fwrite( &mn, 1, sizeof(mn), tvl1 ) ;
                sanity += mn;
                mnDevVector[((((y*GRID_DIVS)+x)*2)+1)] = dev;
                fwrite( &dev, 1, sizeof(dev), tvl1 ) ;
            }
        }
                
        //    std::cout << "The contents of mnDevVector are:";
        //    for (std::vector<float>::iterator it = mnDevVector.begin(); it != mnDevVector.end(); ++it)
        //        std::cout << ' ' << *it;
        //    std::cout << '\n';
        //    std::cout << "The contents of orientedVector are:";
        //    for (std::vector<float>::iterator it = orientedVector.begin(); it != orientedVector.end(); ++it)
        //        std::cout << ' ' << *it;
        //    std::cout << '\n';
        
        counter+=1;
        //    if ((counter%1000)==0) {
        //        ofLogWarning( ofToString(counter) + " --- " + ofToString(ofGetFrameRate()) + " (" + ofToString(((float)counter/(float)totalnumframes)) + "% ) " );
        //    }
        
        if ((counter%1000)==0) {
            ofFile out;
            out.open(actionDir+"tvl1_out.txt", ofFile::Append, false);
            out << (ofToString(counter) + " --- " + ofToString(ofGetFrameRate()) + " (" + ofToString(((float)counter/(float)totalnumframes)) + "% ) val: ") << sanity <<  "\n";
            out.close();
//            fclose(tvl1);
//            ofExit();
        }
        
        
        if ((counter>totalnumframes) && (totalnumframes>0)) {
            fclose(tvl1);
            ofExit();
        }

    }
}

//--------------------------------------------------------------
void avfVideoPlayerApp::draw(){
    int i=0;
    for(auto p : videoPlayers) {
        p->draw(ofMap(i++, 0, videoPlayers.size(), 0, ofGetWidth()), ofGetHeight()/2 - 108*2, 192*4, 108*4);
    }
    colorImg.draw(0, 0);
}

//--------------------------------------------------------------
void avfVideoPlayerApp::keyPressed(int key){
//    switch(key) {
//        case '1':
//            videoPlayers[0]->loadMovie("IntroVideo7.mov");
//            break;
//        case '2':
//            videoPlayers[1]->loadMovie("TheLumineers_1.mov");
//            break;
//        case '3':
//            videoPlayers[2]->loadMovie("EmeliSande_NextToMe.mov");
//            break;
//        case '4':
//            videoPlayers[3]->loadMovie("iHRMF2012_SwedishHouseMafia_DontWorryChild.mov");
//            break;
//    }
////    videoPlayer2.loadMovie("IntroVideo7.mov");
}

//--------------------------------------------------------------
void avfVideoPlayerApp::keyReleased(int key){

}

//--------------------------------------------------------------
void avfVideoPlayerApp::mouseMoved(int x, int y ){

}

//--------------------------------------------------------------
void avfVideoPlayerApp::mouseDragged(int x, int y, int button){

}

//--------------------------------------------------------------
void avfVideoPlayerApp::mousePressed(int x, int y, int button){

}

//--------------------------------------------------------------
void avfVideoPlayerApp::mouseReleased(int x, int y, int button){

}

//--------------------------------------------------------------
void avfVideoPlayerApp::windowResized(int w, int h){

}

//--------------------------------------------------------------
void avfVideoPlayerApp::gotMessage(ofMessage msg){

}

//--------------------------------------------------------------
void avfVideoPlayerApp::dragEvent(ofDragInfo dragInfo){ 

}