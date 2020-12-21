/* R2D2 Pitch Processing
 * 
 * Audio analysis for pitch extraction 
 * 
 * Looks for FFT bin with highest energy. Quite naive...
 *
 * L. Anton-Canalis (info@luisanton.es) 
 */

class PitchDetectorFFT implements AudioListener { 
  float sample_rate = 0;
  float last_period = 0;
  float current_frequency = 0;
  long t;
  
  FFT fft;
  
  final float F0min = 50;
  final float F0max = 400;
   
   
  PitchDetectorFFT () {
  }
  
  void ConfigureFFT (int bufferSize, float s) {
       fft = new FFT(bufferSize, s); 
       fft.window(FFT.HAMMING);
       SetSampleRate(s);
  }
  
  synchronized void StoreFrequency(float f) {
    current_frequency = f;
  }
  
  synchronized float GetFrequency() {
    return current_frequency;
  }
  
  void SetSampleRate(float s) {
     sample_rate = s;
     t = 0;
  }
  
  synchronized void samples(float[] samp) {
    FFT(samp);
  }
  
  synchronized void samples(float[] sampL, float[] sampR) {
    FFT(sampL);
  }
  
  synchronized long GetTime() {
    return t;
  }
  float ave_amplitude=0;
 
  void FFT (float []audio) {
    t++;
    float highest = 0;
    int highest_bin = 0;
    fft.forward(audio);
    int max_bin =  fft.freqToIndex(10000.0f);
    int[] binWindow = {12,13,14,15,16,17,18,19,20,21,22,23};
    float[] scaleAmplitude = {0,0,0,0,0,0,0,0,0,0,0,0};
    float[] LRMatrix = {-0.52215349, -0.588719  , -0.33312913, -0.30364494, -0.57270523, -0.56892712, -0.58016585, -0.48690201, -0.3124494, -0.34832098, -0.16292097, -0.46545937};
    float test_value=0;
    //calculate f0
    for (int n = 0; n < max_bin; n++) {       
       if (fft.getBand(n) > highest) {
         highest = fft.getBand(n);
         highest_bin = n;  
       }
    }  
    
    //calculate chroma
    for(int i=0;i<12;i++){
      if(i==0) ave_amplitude=0;
      //if(i==0) {output.print(1);output.print(" ");}
      for(int j=1;j<=5;j++){
        int nbin=binWindow[i]*j;
        scaleAmplitude[i]+=fft.getBand(nbin); 
        println(i,"=",scaleAmplitude[i]);
      }     
      test_value+=LRMatrix[i]*scaleAmplitude[i];
      ave_amplitude+=scaleAmplitude[i];
      //output.print(scaleAmplitude[i]); 
     // output.print(" ");
    }
    ave_amplitude=pow(ave_amplitude,0.5);
    
    output.println();
    output.flush();
    //sigmoid
    
    test_value=1.0/(1+exp(test_value));
    boolean breathornot=false;
    if(test_value>0.5) breathornot=false;
    else breathornot=true;
    
    
    float freq = fft.indexToFreq(highest_bin); //highest_bin * sample_rate / float(audio.length);  
    StoreFrequency(freq);
  }
};
